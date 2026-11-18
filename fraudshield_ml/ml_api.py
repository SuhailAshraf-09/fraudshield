from pathlib import Path
import hmac
import json
import math
import secrets

import joblib
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = ROOT / "ml_models" / "random_forest_v1.joblib"
KEY_FILE = ROOT / ".ml_api_key"

# Local-development authentication key
if not KEY_FILE.exists():
    KEY_FILE.write_text(
        secrets.token_urlsafe(32),
        encoding="utf-8"
    )

API_KEY = KEY_FILE.read_text(encoding="utf-8").strip()

# Load only our own trusted, locally trained model
bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
features = bundle["features"]
threshold = float(bundle["threshold"])

if not 0 <= threshold <= 1:
    raise RuntimeError("Invalid model threshold.")

app = FastAPI(
    title="FraudShield AI ML Service",
    version="0.1.0"
)

class PredictionRequest(BaseModel):
    features: dict[str, float]

def verify_key(x_ml_api_key: str | None = Header(default=None)):
    if not x_ml_api_key or not hmac.compare_digest(
        x_ml_api_key, API_KEY
    ):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

@app.get("/api/v1/ml/health")
def ml_health():
    return {
        "status": "ready",
        "model": "random-forest-v1",
        "features_required": len(features),
        "production_ready": False
    }

@app.post(
    "/api/v1/ml/predict",
    dependencies=[Depends(verify_key)]
)
def predict(request: PredictionRequest):

    supplied = set(request.features)
    required = set(features)

    if supplied != required:
        raise HTTPException(
            status_code=422,
            detail={
                "missing": sorted(required - supplied),
                "unexpected": sorted(supplied - required)
            }
        )

    values = [
        float(request.features[name])
        for name in features
    ]

    if not all(math.isfinite(value) for value in values):
        raise HTTPException(
            status_code=422,
            detail="All features must be finite numbers"
        )

    frame = pd.DataFrame(
        [values],
        columns=features
    )

    score = float(
        model.predict_proba(frame)[0, 1]
    )

    flagged = score >= threshold

    return {
        "model_version": "random-forest-v1",
        "risk_score": round(score, 6),
        "threshold": threshold,
        "classification": (
            "FLAGGED" if flagged else "NOT_FLAGGED"
        ),
        "review_recommended": bool(flagged),
        "production_ready": False,
        "note": "Uncalibrated development model score"
    }
