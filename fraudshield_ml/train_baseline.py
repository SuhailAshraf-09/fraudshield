from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    confusion_matrix
)

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data" / "processed"
MODELS = ROOT / "ml_models"
REPORTS = ROOT / "reports" / "phase3"

MODELS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

# Load training and testing data
train = pd.read_csv(DATA / "train.csv")
test = pd.read_csv(DATA / "test.csv")

features = (
    ["Time", "Amount"]
    + [f"V{i}" for i in range(1, 29)]
)

# Separate features and fraud labels
X_train = train[features]
y_train = train["Class"].astype(int)

X_test = test[features]
y_test = test["Class"].astype(int)

# Validate data
if X_train.isna().any().any() or X_test.isna().any().any():
    raise ValueError("Missing feature values detected.")

if not set(y_train.unique()).issubset({0, 1}):
    raise ValueError("Invalid training labels.")

if not set(y_test.unique()).issubset({0, 1}):
    raise ValueError("Invalid testing labels.")

# Build ML pipeline
model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

print("Training Logistic Regression model...")

# Train on training data only
model.fit(X_train, y_train)

# Evaluate on held-out test data
probabilities = model.predict_proba(X_test)[:, 1]

threshold = 0.5
predictions = (probabilities >= threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test, predictions, labels=[0, 1]
).ravel()

metrics = {
    "model": "Logistic Regression Baseline",
    "training_records": int(len(train)),
    "testing_records": int(len(test)),
    "precision": float(precision_score(
        y_test, predictions, zero_division=0
    )),
    "recall": float(recall_score(
        y_test, predictions, zero_division=0
    )),
    "f1_score": float(f1_score(
        y_test, predictions, zero_division=0
    )),
    "average_precision": float(
        average_precision_score(y_test, probabilities)
    ),
    "threshold": threshold,
    "true_positives": int(tp),
    "false_positives": int(fp),
    "true_negatives": int(tn),
    "false_negatives": int(fn),
    "split_type": "Stratified random holdout"
}

# Save trained model and metrics
joblib.dump(
    model,
    MODELS / "logistic_baseline.joblib"
)

(REPORTS / "baseline_metrics.json").write_text(
    json.dumps(metrics, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - ML TRAINING RESULTS")

for key, value in metrics.items():
    print(f"{key}: {value}")

print("\nModel training completed.")
print("Model saved successfully.")
