from pathlib import Path
import json
import csv

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports" / "phase3"
REPORTS.mkdir(parents=True, exist_ok=True)

models = [
    (
        "Logistic Regression",
        "threshold_validation.json",
        ["validation_precision", "validation_recall",
         "validation_f1", "validation_average_precision"]
    ),
    (
        "XGBoost",
        "xgboost_validation.json",
        ["precision", "recall",
         "f1_score", "average_precision"]
    ),
    (
        "Random Forest",
        "random_forest_validation.json",
        ["precision", "recall",
         "f1_score", "average_precision"]
    ),
    (
        "Isolation Forest",
        "isolation_forest_validation.json",
        ["precision", "recall",
         "f1_score", "average_precision"]
    )
]

results = []

for name, filename, keys in models:
    path = REPORTS / filename

    if not path.exists():
        raise SystemExit(f"Missing report: {filename}")

    data = json.loads(path.read_text(encoding="utf-8"))

    result = {
        "model": name,
        "precision": float(data[keys[0]]),
        "recall": float(data[keys[1]]),
        "f1_score": float(data[keys[2]]),
        "average_precision": float(data[keys[3]])
    }

    results.append(result)

# Save CSV comparison
csv_file = REPORTS / "four_model_comparison.csv"

with csv_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0]))
    writer.writeheader()
    writer.writerows(results)

# Save JSON comparison
json_file = REPORTS / "four_model_comparison.json"

json_file.write_text(
    json.dumps({
        "comparison_type": "exploratory_validation",
        "production_ready": False,
        "results": results
    }, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - FOUR MODEL COMPARISON")

for row in results:
    print("\nModel:", row["model"])
    for metric in [
        "precision", "recall",
        "f1_score", "average_precision"
    ]:
        print(
            metric,
            f"{row[metric] * 100:.2f}%"
        )

print("\nModels compared:", len(results))
print("Comparison report generated successfully!")
