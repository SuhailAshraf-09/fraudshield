from pathlib import Path
import json
import numpy as np
import pandas as pd

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_recall_curve,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    confusion_matrix
)

ROOT = Path(__file__).resolve().parent.parent
TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
MODELS = ROOT / "ml_models"
REPORTS = ROOT / "reports" / "phase3"

MODELS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

if not TRAIN_FILE.exists():
    raise SystemExit("Training dataset not found.")

# Load training data only
df = pd.read_csv(TRAIN_FILE)

features = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

X = df[features]
y = df["Class"].astype(int)

# Create internal validation data
X_fit, X_val, y_fit, y_val = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=123
)

# Handle fraud class imbalance
normal_count = int((y_fit == 0).sum())
fraud_count = int((y_fit == 1).sum())

if fraud_count == 0:
    raise SystemExit("No fraud records in training data.")

weight = normal_count / fraud_count

# Initialize XGBoost classifier
model = XGBClassifier(
    objective="binary:logistic",
    eval_metric="aucpr",
    n_estimators=240,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=weight,
    tree_method="hist",
    early_stopping_rounds=20,
    random_state=42,
    n_jobs=2
)

print("Training XGBoost Fraud Detection Model...")

model.fit(
    X_fit, y_fit,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# Validation scores
scores = model.predict_proba(X_val)[:, 1]

precision, recall, thresholds = precision_recall_curve(
    y_val, scores
)

f1_values = (
    2 * precision[:-1] * recall[:-1]
    / (precision[:-1] + recall[:-1] + 1e-12)
)

best_index = int(np.argmax(f1_values))
threshold = float(thresholds[best_index])

predictions = (scores >= threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_val, predictions, labels=[0, 1]
).ravel()

results = {
    "model": "XGBoost Fraud Detection",
    "model_version": "xgboost-v1",
    "training_records": len(X_fit),
    "validation_records": len(X_val),
    "selected_threshold": threshold,
    "precision": float(precision_score(
        y_val, predictions, zero_division=0
    )),
    "recall": float(recall_score(
        y_val, predictions, zero_division=0
    )),
    "f1_score": float(f1_score(
        y_val, predictions, zero_division=0
    )),
    "average_precision": float(
        average_precision_score(y_val, scores)
    ),
    "true_positives": int(tp),
    "false_positives": int(fp),
    "true_negatives": int(tn),
    "false_negatives": int(fn),
    "best_iteration": int(model.best_iteration),
    "test_dataset_used": False,
    "production_ready": False
}

# Save model in XGBoost's native JSON format
model.save_model(
    str(MODELS / "xgboost_fraud_v1.json")
)

# Save model feature ordering
(REPORTS / "xgboost_features.json").write_text(
    json.dumps(features, indent=2),
    encoding="utf-8"
)

# Save validation results
(REPORTS / "xgboost_validation.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - XGBOOST RESULTS")

for key, value in results.items():
    print(f"{key}: {value}")

print("\nXGBoost training completed.")
print("Model and reports saved successfully.")
