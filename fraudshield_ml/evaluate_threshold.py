from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score,
    f1_score, confusion_matrix
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports" / "phase3"

REPORTS.mkdir(parents=True, exist_ok=True)

train = pd.read_csv(DATA / "train.csv")
test = pd.read_csv(DATA / "test.csv")

features = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

X = train[features]
y = train["Class"].astype(int)

X_fit, X_val, y_fit, y_val = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=123
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

model.fit(X_fit, y_fit)

validation_scores = model.predict_proba(X_val)[:, 1]

from sklearn.metrics import precision_recall_curve

p, r, thresholds = precision_recall_curve(
    y_val, validation_scores
)

f1 = 2 * p[:-1] * r[:-1] / (
    p[:-1] + r[:-1] + 1e-12
)

threshold = float(thresholds[np.argmax(f1)])

X_test = test[features]
y_test = test["Class"].astype(int)

test_scores = model.predict_proba(X_test)[:, 1]

results = {}

for name, cutoff in [
    ("default_0_5", 0.5),
    ("validation_selected", threshold)
]:
    predictions = (test_scores >= cutoff).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    results[name] = {
        "threshold": cutoff,
        "precision": float(precision_score(
            y_test, predictions, zero_division=0
        )),
        "recall": float(recall_score(
            y_test, predictions, zero_division=0
        )),
        "f1": float(f1_score(
            y_test, predictions, zero_division=0
        )),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn)
    }

output = REPORTS / "threshold_test_evaluation.json"
output.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - TEST EVALUATION")

for name, metrics in results.items():
    print("\n", name)
    for key, value in metrics.items():
        print(f"{key}: {value}")

print("\nEvaluation completed successfully.")
print("Report saved:", output)
