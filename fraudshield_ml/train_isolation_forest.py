from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
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

# Load training dataset
df = pd.read_csv(DATA)

features = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

X = df[features]
y = df["Class"].astype(int)

# Create separate fitting and validation sets
X_fit, X_val, y_fit, y_val = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=123
)

# Select legitimate transactions for model fitting
normal_data = X_fit.loc[y_fit == 0]

sample_size = min(50000, len(normal_data))
normal_sample = normal_data.sample(
    n=sample_size,
    random_state=42
)

# Initialize anomaly detection model
model = IsolationForest(
    n_estimators=150,
    max_samples=256,
    contamination="auto",
    random_state=42,
    n_jobs=2
)

print("Training Isolation Forest Model...")
model.fit(normal_sample)

# Higher transformed scores mean more anomalous
fit_scores = -model.score_samples(normal_sample)

# Select an anomaly cutoff using fitting data only
threshold = float(np.quantile(fit_scores, 0.995))

# Evaluate on separate validation data
scores = -model.score_samples(X_val)
predictions = (scores > threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_val, predictions, labels=[0, 1]
).ravel()

results = {
    "model": "Isolation Forest",
    "model_version": "isolation-forest-v1",
    "training_normal_records": int(sample_size),
    "validation_records": int(len(y_val)),
    "anomaly_threshold": threshold,
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

# Save trained model and its configuration
joblib.dump(
    {
        "model": model,
        "features": features,
        "threshold": threshold
    },
    MODELS / "isolation_forest_v1.joblib"
)

# Save validation report
output = REPORTS / "isolation_forest_validation.json"

output.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - ISOLATION FOREST RESULTS")

for key, value in results.items():
    print(f"{key}: {value}")

print("\nIsolation Forest training completed.")
print("Model saved successfully.")
print("Report saved:", output)
