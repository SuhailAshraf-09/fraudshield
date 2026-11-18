from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

ARTIFACT = ROOT / "ml_models" / "random_forest_v1.joblib"
TEST_CSV = ROOT / "data" / "processed" / "test.csv"
REPORT = ROOT / "reports" / "phase4" / "inference_smoke_test.json"

if not ARTIFACT.is_file() or not TEST_CSV.is_file():
    raise SystemExit("Model artifact or test.csv not found.")

# Load only trusted locally trained model files
bundle = joblib.load(ARTIFACT)

model = bundle["model"]
features = bundle["features"]
threshold = float(bundle["threshold"])

expected = {"Time", "Amount"} | {
    f"V{i}" for i in range(1, 29)
}

if len(features) != 30 or set(features) != expected:
    raise SystemExit("Invalid model feature schema.")

if not 0 <= threshold <= 1:
    raise SystemExit("Invalid threshold.")

# Load existing test transactions
df = pd.read_csv(TEST_CSV)

if not {"Class", *features}.issubset(df.columns):
    raise SystemExit("Required columns are missing.")

normal = df[df["Class"] == 0].head(1)
fraud = df[df["Class"] == 1].head(1)

if normal.empty or fraud.empty:
    raise SystemExit("Both classes are required.")

samples = pd.concat(
    [normal, fraud],
    ignore_index=True
)

X = samples[features].apply(
    pd.to_numeric, errors="raise"
)

if not np.isfinite(X.to_numpy(dtype=float)).all():
    raise SystemExit("Invalid numerical values.")

# Generate fraud classification scores
scores = model.predict_proba(X)[:, 1]

results = []

for actual, score in zip(
    samples["Class"].astype(int), scores
):
    results.append({
        "actual_class": int(actual),
        "model_score": round(float(score), 6),
        "predicted_class": int(score >= threshold)
    })

REPORT.parent.mkdir(parents=True, exist_ok=True)

REPORT.write_text(
    json.dumps({
        "model": "random_forest_v1",
        "threshold": threshold,
        "purpose": "Local inference smoke test",
        "samples": results
    }, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - MODEL INFERENCE")

print("Model loaded successfully")
print("Features:", len(features))
print("Decision threshold:", threshold)

for result in results:
    print(result)

print("\nInference test completed.")
print("Report saved:", REPORT)
