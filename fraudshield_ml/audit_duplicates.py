from pathlib import Path
import pandas as pd
import json

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data" / "raw" / "creditcard.csv"
REPORT = ROOT / "reports" / "phase2"

REPORT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA)

duplicates = df.duplicated(keep="first")

duplicate_counts = (
    df.loc[duplicates, "Class"]
    .value_counts()
    .reindex([0, 1], fill_value=0)
)

report = {
    "total_transactions": int(len(df)),
    "duplicate_rows": int(duplicates.sum()),
    "normal_duplicates": int(duplicate_counts[0]),
    "fraud_duplicates": int(duplicate_counts[1]),
    "rows_if_duplicates_removed": int(
        len(df) - duplicates.sum()
    ),
    "raw_dataset_modified": False
}

output = REPORT / "duplicate_audit.json"

output.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - DUPLICATE AUDIT")

for key, value in report.items():
    print(f"{key}: {value}")

print("\nReport saved:", output)
