from pathlib import Path
import json
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "creditcard.csv"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports" / "phase2"

PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

# Load the real financial transaction dataset
if not RAW.exists():
    raise SystemExit("Real creditcard.csv file not found.")

df = pd.read_csv(RAW)

# Verify dataset structure and labels
required = (
    ["Time"]
    + [f"V{i}" for i in range(1, 29)]
    + ["Amount", "Class"]
)

if not set(required).issubset(df.columns):
    raise SystemExit("Required dataset columns missing.")

if df[required].isna().any().any():
    raise SystemExit("Dataset contains missing values.")

if not df["Class"].isin([0, 1]).all():
    raise SystemExit("Invalid fraud classification labels.")

original_rows = len(df)

# Create a separate deduplicated baseline dataset
df_clean = df.drop_duplicates().copy()
removed = original_rows - len(df_clean)

# Stratified train/test splitting
train_df, test_df = train_test_split(
    df_clean,
    test_size=0.20,
    random_state=42,
    stratify=df_clean["Class"]
)

# Save independent datasets
train_df.to_csv(
    PROCESSED / "train.csv",
    index=False
)

test_df.to_csv(
    PROCESSED / "test.csv",
    index=False
)

# Generate preprocessing summary
summary = {
    "original_rows": original_rows,
    "duplicates_removed": removed,
    "clean_rows": len(df_clean),
    "train_rows": len(train_df),
    "test_rows": len(test_df),
    "train_fraud": int(train_df["Class"].sum()),
    "test_fraud": int(test_df["Class"].sum()),
    "split_method": "Stratified random 80/20",
    "raw_dataset_modified": False,
    "model_trained": False
}

(REPORTS / "preprocessing_summary.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - DATA PREPROCESSING")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nPreprocessing completed successfully.")
