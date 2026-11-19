import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    roc_auc_score
)

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "ml_models/random_forest_v1.joblib"
TEST = ROOT / "data/processed/test.csv"

print("\nFRAUDSHIELD AI - FINAL ML EVALUATION")

if not MODEL.is_file() or not TEST.is_file():
    raise SystemExit(
        "SAFETY STOP: Model or test dataset missing."
    )

# Load only the project's trusted local model.
bundle = joblib.load(MODEL)

model = bundle["model"]
features = list(bundle["features"])
threshold = float(bundle["threshold"])

expected = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

if features != expected:
    raise SystemExit("Invalid model feature schema.")

if not 0 <= threshold <= 1:
    raise SystemExit("Invalid model threshold.")

df = pd.read_csv(TEST, usecols=features + ["Class"])

if df.empty or df.isna().any().any():
    raise SystemExit("Invalid or empty test dataset.")

if not df["Class"].isin([0, 1]).all():
    raise SystemExit("Invalid classification labels.")

X = df[features].astype(float)
y = df["Class"].astype(int)

if not np.isfinite(X.to_numpy()).all():
    raise SystemExit("Non-finite feature values detected.")

if sorted(model.classes_.tolist()) != [0, 1]:
    raise SystemExit("Unexpected model classes.")

fraud_index = list(model.classes_).index(1)
scores = model.predict_proba(X)[:, fraud_index]

predictions = (scores >= threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y, predictions, labels=[0, 1]
).ravel()

results = {
    "model": "random-forest-v1",
    "evaluation_type": "held-out_test",
    "test_records": int(len(y)),
    "actual_fraud_records": int(y.sum()),
    "threshold": threshold,
    "precision": float(precision_score(
        y, predictions, zero_division=0
    )),
    "recall": float(recall_score(
        y, predictions, zero_division=0
    )),
    "f1_score": float(f1_score(
        y, predictions, zero_division=0
    )),
    "pr_auc_average_precision": float(
        average_precision_score(y, scores)
    ),
    "roc_auc": float(roc_auc_score(y, scores)),
    "false_positive_rate": float(
        fp / (fp + tn) if fp + tn else 0
    ),
    "true_positive": int(tp),
    "false_positive": int(fp),
    "true_negative": int(tn),
    "false_negative": int(fn),
    "model_retrained": False,
    "database_modified": False,
    "production_ready": False
}

report_dir = ROOT / "reports/phase10"
report_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now(
    timezone.utc
).strftime("%Y%m%d_%H%M%S_%f")

report = report_dir / (
    f"final_ml_evaluation_{timestamp}.json"
)

with report.open("x", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

for key, value in results.items():
    print(f"{key}: {value}")

print("\nReport:", report)
print("FINAL ML EVALUATION COMPLETED!")
