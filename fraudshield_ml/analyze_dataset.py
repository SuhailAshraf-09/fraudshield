from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Project locations
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "creditcard.csv"
DEMO = ROOT / "data" / "demo" / "synthetic_creditcard.csv"
REPORTS = ROOT / "reports" / "phase2"

REPORTS.mkdir(parents=True, exist_ok=True)

# Generate demonstration data if real data is unavailable
def make_demo():
    DEMO.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n = 3000

    data = {
        "Time": np.sort(rng.integers(0, 172800, n)),
        **{f"V{i}": rng.normal(0, 1, n)
           for i in range(1, 29)},
        "Amount": np.round(
            rng.lognormal(3.5, 1.1, n), 2
        )
    }

    data["Class"] = np.zeros(n, dtype=int)
    fraud_rows = rng.choice(n, size=30, replace=False)
    data["Class"][fraud_rows] = 1

    data["V1"][fraud_rows] -= 2.5
    data["V2"][fraud_rows] += 1.8

    pd.DataFrame(data).to_csv(DEMO, index=False)
    return DEMO

# Load the real CSV when present; otherwise use demo data
source = RAW if RAW.is_file() else make_demo()
is_demo = source == DEMO

df = pd.read_csv(source)

# Check dataset structure
required = (
    ["Time"]
    + [f"V{i}" for i in range(1, 29)]
    + ["Amount", "Class"]
)

missing_columns = [
    col for col in required if col not in df.columns
]

if missing_columns:
    raise SystemExit(
        f"Missing dataset columns: {missing_columns}"
    )

# Validate fraud labels
classes = pd.to_numeric(df["Class"], errors="coerce")

if classes.isna().any() or not classes.isin([0, 1]).all():
    raise SystemExit("Class must contain only 0 or 1.")

counts = classes.astype(int).value_counts().reindex(
    [0, 1], fill_value=0
)

# Analyze data quality
missing_values = df.isna().sum()
duplicates = int(df.duplicated().sum())

fraud_rate = (
    float(counts.loc[1] / len(df) * 100)
    if len(df) else 0.0
)

summary = {
    "dataset_type": "SYNTHETIC DEMO" if is_demo else "REAL CSV",
    "rows": int(len(df)),
    "columns": int(len(df.columns)),
    "normal_transactions": int(counts.loc[0]),
    "fraud_transactions": int(counts.loc[1]),
    "fraud_percentage": round(fraud_rate, 4),
    "missing_cells": int(missing_values.sum()),
    "duplicate_rows": duplicates
}

# Generate statistical reports
(REPORTS / "summary.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

missing_values.to_csv(REPORTS / "missing_values.csv")

counts.to_csv(REPORTS / "class_distribution.csv")

df.assign(Class=classes.astype(int)).groupby(
    "Class"
)["Amount"].agg(
    ["count", "mean", "median", "min", "max"]
).round(2).to_csv(REPORTS / "amount_by_class.csv")

# Generate analytics chart
plt.figure(figsize=(7, 4))
plt.bar(
    ["Normal (0)", "Fraud (1)"],
    counts.values
)
plt.title("Fraud vs Normal Transactions")
plt.ylabel("Number of Transactions")
plt.tight_layout()
plt.savefig(
    REPORTS / "class_distribution.png",
    dpi=150
)
plt.close()

# Display results
print("\nFRAUDSHIELD AI - PHASE 2 REPORT")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nReports saved:", REPORTS)
print("No machine learning model trained yet.")
