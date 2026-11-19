import json
import math
from datetime import datetime, timezone
from uuid import uuid4, uuid5, NAMESPACE_URL

import pandas as pd

from fastapi import (
    APIRouter, Depends, HTTPException
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Transaction, Prediction, Alert
from app.security import reviewer_or_admin
from app.ml_integrated_router import FEATURES, load_model


router = APIRouter(tags=["ML Prediction Storage"])

MODEL_VERSION = "random-forest-v1"


class PredictAndSaveRequest(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=100)
    amount_minor: int = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    occurred_at: datetime
    features: dict[str, float]


def validate_features(values):
    expected = set(FEATURES)
    received = set(values)

    if expected != received:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Invalid ML feature schema",
                "missing": sorted(expected - received),
                "unexpected": sorted(received - expected)
            }
        )

    if not all(
        math.isfinite(float(values[name]))
        for name in FEATURES
    ):
        raise HTTPException(
            status_code=422,
            detail="ML features must be finite numbers."
        )


def build_record(model_class, values):
    table = model_class.__table__

    allowed = {
        col.name for col in table.columns
    }

    record = {
        name: value
        for name, value in values.items()
        if name in allowed
    }

    missing = [
        col.name
        for col in table.columns
        if (
            not col.nullable
            and not col.primary_key
            and col.default is None
            and col.server_default is None
            and col.name not in record
        )
    ]

    if missing:
        raise RuntimeError(
            f"{table.name}: unmapped required fields: {missing}"
        )

    return model_class(**record)


@router.post("/predict-and-save")
def predict_and_save(
    request: PredictAndSaveRequest,
    db: Session = Depends(get_db),
    user=Depends(reviewer_or_admin)
):
    validate_features(request.features)

    if request.occurred_at.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="occurred_at must include a timezone."
        )

    if (
        len(request.currency) != 3
        or not request.currency.isalpha()
        or not request.currency.isupper()
    ):
        raise HTTPException(
            status_code=422,
            detail="Currency must be a 3-letter uppercase code."
        )

    # FRAUDSHIELD STABLE TX ID V1
    stable_tx_id = str(uuid5(
        NAMESPACE_URL,
        "fraudshield-ai/ml/predict-and-save:"
        + request.transaction_id
    ))

    existing = db.query(Transaction).filter(
        Transaction.id == stable_tx_id
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Transaction identifier already exists."
        )

    model, threshold = load_model()

    input_frame = pd.DataFrame(
        [{
            name: float(request.features[name])
            for name in FEATURES
        }],
        columns=FEATURES
    )

    model_score = float(
        model.predict_proba(input_frame)[0][1]
    )

    flagged = model_score >= float(threshold)
    tier = "HIGH" if flagged else "LOW"

    now = datetime.now(timezone.utc)

    transaction_values = {
        "id": stable_tx_id,
        "amount_minor": request.amount_minor,
        "currency": request.currency,
        "occurred_at": request.occurred_at,
        "created_at": now
    }

    prediction_values = {
        "id": str(uuid4()),
        "model_version": MODEL_VERSION,
        "risk_index": model_score * 100,
        "risk_tier": tier,
        "requires_review": flagged,
        "reasons_json": json.dumps({
            "model_version": MODEL_VERSION,
            "model_score": model_score,
            "threshold": float(threshold),
            "classification": (
                "FLAGGED" if flagged else "NOT_FLAGGED"
            ),
            "production_ready": False
        }),
        "created_at": now
    }

    try:
        tx = build_record(
            Transaction,
            transaction_values
        )

        db.add(tx)
        db.flush()

        prediction_values["transaction_id"] = tx.id

        prediction = build_record(
            Prediction,
            prediction_values
        )

        db.add(prediction)

        if flagged:
            alert = build_record(
                Alert,
                {
                    "id": str(uuid4()),
                    "transaction_id": tx.id,
                    "status": "open",
                    "priority": "high",
                    "notes": (
                        "Random Forest model flagged "
                        "this transaction for review."
                    ),
                    "created_at": now
                }
            )

            db.add(alert)

        db.commit()
        db.refresh(prediction)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database record conflict."
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Prediction storage failed."
        )

    return {
        "transaction_id": request.transaction_id,
        "prediction_id": prediction.id,
        "model_version": MODEL_VERSION,
        "model_score": round(model_score, 6),
        "threshold": float(threshold),
        "classification": (
            "FLAGGED" if flagged else "NOT_FLAGGED"
        ),
        "risk_tier": tier,
        "requires_review": flagged,
        "saved_to_database": True,
        "production_ready": False
    }
