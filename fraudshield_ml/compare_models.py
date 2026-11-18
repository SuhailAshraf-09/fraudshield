from pathlib import Path
import json
import csv

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports" / "phase3"

models = [
    {
        "name": "Logistic Regression",
        "file": "threshold_validation.json",
        "keys": [
            "validation_precision",
            "validation_recall",
            "validation_f1",
            "validation_average_precision"
        ]
    },
    {
        "name": "XGBoost",
        "file": "xgboost_validation.json",
        "keys": [
            "precision", "recall",
            "f1_score", "average_precision"
        ]
    },
    {
        "name": "Random Forest",
        "file": "random_forest_validation.json",
        "keys": [
            "precision", "recall",
            "f1_score", "average_precision"
        ]
    }
]

results = []

for item in models:
    path = REPORTS / item["file"]

    if not path.exists():
        print("Missing report:", path.name)
        continue

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    keys = item["keys"]

    results.append({
        "model": item["name"],
        "precision": float(data[keys[0]]),
        "recall": float(data[keys[1]]),
        "f1_score": float(data[keys[2]]),
        "average_precision": float(data[keys[3]])
    })

if not results:
    raise SystemExit("No model reports found.")

print("\nFRAUDSHIELD AI - MODEL COMPARISON")

for model in results:
    print("\nModel:", model["model"])
    for metric in [
        "precision", "recall",
        "f1_score", "average_precision"
    ]:
        print(
            metric,
            round(model[metric] * 100, 2),
            "%"
        )

# Save comparison reports
csv_path = REPORTS / "model_comparison.csv"

with csv_path.open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file, fieldnames=[
            "model", "precision", "recall",
            "f1_score", "average_precision"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

json_path = REPORTS / "model_comparison.json"

json_path.write_text(
    json.dumps({
        "comparison_type": "development_validation",
        "results": results,
        "production_ready": False
    }, indent=2),
    encoding="utf-8"
)

print("\nModels compared:", len(results))
print("Comparison report generated successfully.")
