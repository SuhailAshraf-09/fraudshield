import io
import numpy as np
import pandas as pd

from fastapi import (
    APIRouter, Depends, File, UploadFile, HTTPException
)

from app.security import reviewer_or_admin
from app.ml_integrated_router import load_model, FEATURES

router = APIRouter(
    prefix="/api/v1/ml",
    tags=["Machine Learning"]
)

MAX_FILE_SIZE = 1000000
MAX_ROWS = 200


@router.post("/batch-predict")
async def batch_predict(
    file: UploadFile = File(...),
    user=Depends(reviewer_or_admin)
):
    # Verify file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(422, "CSV file required")

    # Enforce application-level file size limit
    raw = await file.read(MAX_FILE_SIZE + 1)

    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(413, "CSV exceeds size limit")

    # Load CSV records
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except (
        ValueError,
        UnicodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError
    ):
        raise HTTPException(422, "Invalid CSV data")

    if not 1 <= len(df) <= MAX_ROWS:
        raise HTTPException(
            422,
            "CSV must contain 1 to 200 transactions"
        )

    if len(df.columns) != len(FEATURES) or set(df.columns) != set(FEATURES):
        raise HTTPException(
            422,
            "Expected Time, Amount and V1-V28 columns"
        )

    # Convert data into numerical features
    try:
        X = df[FEATURES].apply(
            pd.to_numeric,
            errors="raise"
        ).astype("float64")
    except (ValueError, TypeError, OverflowError):
        raise HTTPException(422, "Invalid numerical values")

    if not np.isfinite(X.to_numpy()).all():
        raise HTTPException(
            422,
            "Missing or non-finite values detected"
        )

    # Run trained Random Forest inference
    model, threshold = load_model()
    scores = model.predict_proba(X)[:, 1]

    predictions = []

    for index, score in enumerate(scores):
        score = float(score)
        flagged = score >= threshold

        predictions.append({
            "row_number": index + 1,
            "model_score": round(score, 6),
            "classification": (
                "FLAGGED" if flagged else "NOT_FLAGGED"
            ),
            "review_recommended": bool(flagged)
        })

    flagged_count = sum(
        item["review_recommended"]
        for item in predictions
    )

    return {
        "model_version": "random-forest-v1",
        "total_transactions": len(predictions),
        "flagged_transactions": flagged_count,
        "not_flagged_transactions": (
            len(predictions) - flagged_count
        ),
        "predictions": predictions,
        "production_ready": False,
        "note": "Uncalibrated development scores"
    }
