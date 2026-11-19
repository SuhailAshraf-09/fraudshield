"""Authenticated Random Forest evaluation metadata API."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.security import current_user

router = APIRouter(
    prefix="/api/v1/ml/model",
    tags=["Machine Learning Metadata"]
)

ROOT = Path(__file__).resolve().parent.parent

METRICS_FILE = (
    ROOT / "ml_models" / "random_forest_v1_metrics.json"
)


@router.get("/metrics")
def model_performance(user=Depends(current_user)):
    """Return verified held-out Random Forest evaluation metrics."""

    try:
        data = json.loads(
            METRICS_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=503,
            detail="ML evaluation metadata unavailable."
        ) from exc

    if (
        not isinstance(data, dict)
        or data.get("model_version") != "random-forest-v1"
        or data.get("evaluation_type") != "held_out_test"
        or data.get("production_ready") is not False
    ):
        raise HTTPException(
            status_code=503,
            detail="ML evaluation metadata invalid."
        )

    required = (
        "test_records",
        "decision_threshold",
        "precision",
        "recall",
        "f1_score",
        "average_precision",
        "roc_auc",
        "false_positive_rate"
    )

    if any(key not in data for key in required):
        raise HTTPException(
            status_code=503,
            detail="Incomplete evaluation metadata."
        )

    for key in required[1:]:
        value = data[key]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 1
        ):
            raise HTTPException(
                status_code=503,
                detail="Invalid ML evaluation metric."
            )

    if (
        type(data["test_records"]) is not int
        or data["test_records"] <= 0
    ):
        raise HTTPException(
            status_code=503,
            detail="Invalid evaluation record count."
        )

    return data
