from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
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
DATA = ROOT / "data" / "processed" / "train.csv"
MODELS = ROOT / "ml_models"
REPORTS = ROOT / "reports" / "phase3"

MODELS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

if not DATA.exists():
    raise SystemExit("Training dataset not found.")

df = pd.read_csv(DATA)

features = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

X = df[features]
y = df["Class"].astype(int)

# Split training data into fitting and validation subsets
X_fit, X_val, y_fit, y_val = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=123
)

# Initialize Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=12,
    min_samples_leaf=2,
    max_samples=0.7,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

print("Training Random Forest Fraud Detection Model...")

model.fit(X_fit, y_fit)

scores = model.predict_proba(X_val)[:, 1]

# Select validation threshold
precision, recall, thresholds = precision_recall_curve(
    y_val, scores
)

f1_values = (
    2 * precision[:-1] * recall[:-1]
    / (precision[:-1] + recall[:-1] + 1e-12)
)

index = int(np.argmax(f1_values))
threshold = float(thresholds[index])

predictions = (scores >= threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_val, predictions, labels=[0, 1]
).ravel()

results = {
    "model": "Random Forest",
    "version": "random-forest-v1",
    "validation_records": int(len(y_val)),
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
    "test_dataset_used": False,
    "production_ready": False
}

joblib.dump(
    {"model": model, "features": features,
     "threshold": threshold},
    MODELS / "random_forest_v1.joblib"
)

(REPORTS / "random_forest_validation.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - RANDOM FOREST RESULTS")

for key, value in results.items():
    print(f"{key}: {value}")

print("\nRandom Forest training completed.")
