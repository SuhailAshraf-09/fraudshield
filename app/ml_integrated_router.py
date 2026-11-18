from pathlib import Path
from functools import lru_cache
import math

import joblib
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security import reviewer_or_admin

ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = ROOT / "ml_models" / "random_forest_v1.joblib"

FEATURES = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

router = APIRouter(
    prefix="/api/v1/ml",
    tags=["Machine Learning"]
)

class MLRequest(BaseModel):
    features: dict[str, float]


@lru_cache(maxsize=1)
def load_model():
    # Load only the trusted, locally trained model
    bundle = joblib.load(MODEL_FILE)

    model = bundle["model"]
    feature_names = list(bundle["features"])
    threshold = float(bundle["threshold"])

    if feature_names != FEATURES:
        raise RuntimeError("Model feature mismatch.")

    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise RuntimeError("Invalid model threshold.")

    return model, threshold


@router.post("/predict")
def predict_ml(
    request: MLRequest,
    user=Depends(reviewer_or_admin)
):
    supplied = set(request.features)
    required = set(FEATURES)

    if supplied != required:
        raise HTTPException(
            status_code=422,
            detail={
                "missing": sorted(required - supplied),
                "unexpected": sorted(supplied - required)
            }
        )

    values = [
        request.features[name]
        for name in FEATURES
    ]

    if not all(math.isfinite(v) for v in values):
        raise HTTPException(
            status_code=422,
            detail="Features must be finite numerical values."
        )

    model, threshold = load_model()

    frame = pd.DataFrame(
        [values],
        columns=FEATURES
    )

    score = float(
        model.predict_proba(frame)[0, 1]
    )

    flagged = score >= threshold

    return {
        "model_version": "random-forest-v1",
        "model_score": round(score, 6),
        "decision_threshold": threshold,
        "classification": (
            "FLAGGED" if flagged else "NOT_FLAGGED"
        ),
        "review_recommended": bool(flagged),
        "production_ready": False,
        "note": "Uncalibrated ML development score"
    }
