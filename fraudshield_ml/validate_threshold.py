from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_recall_curve,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed" / "train.csv"
REPORT = ROOT / "reports" / "phase3"

REPORT.mkdir(parents=True, exist_ok=True)

# Load existing training dataset
df = pd.read_csv(DATA)

features = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

X = df[features]
y = df["Class"].astype(int)

# Separate training and validation data
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=123
)

# Create the machine learning pipeline
model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

print("Training validation model...")
model.fit(X_train, y_train)

# Generate validation scores
scores = model.predict_proba(X_val)[:, 1]

precision, recall, thresholds = precision_recall_curve(
    y_val, scores
)

# Select threshold using validation F1-score
f1_values = (
    2 * precision[:-1] * recall[:-1]
    / (precision[:-1] + recall[:-1] + 1e-12)
)

best_index = int(np.argmax(f1_values))
best_threshold = float(thresholds[best_index])

predictions = (scores >= best_threshold).astype(int)

# Calculate validation metrics
result = {
    "model": "Logistic Regression Validation",
    "selected_threshold": best_threshold,
    "validation_precision": float(
        precision_score(y_val, predictions, zero_division=0)
    ),
    "validation_recall": float(
        recall_score(y_val, predictions, zero_division=0)
    ),
    "validation_f1": float(
        f1_score(y_val, predictions, zero_division=0)
    ),
    "validation_average_precision": float(
        average_precision_score(y_val, scores)
    ),
    "test_dataset_used": False,
    "production_ready": False
}

# Save validation results
output = REPORT / "threshold_validation.json"

output.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - THRESHOLD VALIDATION")

for key, value in result.items():
    print(f"{key}: {value}")

print("\nValidation completed successfully.")
print("Report saved:", output)
