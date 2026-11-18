import io
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from fastapi import (
    APIRouter, Depends, File,
    UploadFile, HTTPException, Response
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph,
    Spacer, Table, TableStyle
)

from app.security import reviewer_or_admin
from app.ml_integrated_router import load_model, FEATURES

router = APIRouter(
    prefix="/api/v1/ml",
    tags=["Machine Learning Reports"]
)

MAX_BYTES = 1000000
MAX_ROWS = 200


def generate_pdf(predictions, threshold):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    navy = colors.HexColor("#10243A")
    gold = colors.HexColor("#B89642")

    story.append(Paragraph(
        "<b>FRAUDSHIELD AI</b>",
        styles["Title"]
    ))

    story.append(Paragraph(
        "Financial Transaction Fraud Investigation Report",
        styles["Heading2"]
    ))

    story.append(Spacer(1, 12))

    generated = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")

    total = len(predictions)
    flagged = sum(
        item["review_recommended"]
        for item in predictions
    )

    summary = [
        ["Report Information", "Value"],
        ["Model", "Random Forest v1"],
        ["Generated", generated],
        ["Transactions analyzed", str(total)],
        ["Flagged transactions", str(flagged)],
        ["Not flagged", str(total - flagged)],
        ["Decision threshold", f"{threshold:.6f}"]
    ]

    summary_table = Table(
        summary,
        colWidths=[200, 280],
        repeatRows=1
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph(
        "Transaction Investigation Results",
        styles["Heading2"]
    ))

    rows = [[
        "Row", "Model Score",
        "Classification", "Review"
    ]]

    for item in predictions:
        rows.append([
            str(item["row_number"]),
            f'{item["model_score"]:.6f}',
            item["classification"],
            "YES" if item["review_recommended"] else "NO"
        ])

    result_table = Table(
        rows,
        colWidths=[60, 105, 190, 125],
        repeatRows=1,
        hAlign="LEFT"
    )

    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F2F4F7")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    story.append(result_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph(
        "<b>Important:</b> This report uses an "
        "uncalibrated development ML model. "
        "A flagged transaction requires human review. "
        "The model score is not a verified fraud probability. "
        "This report is not production-certified.",
        styles["Normal"]
    ))

    doc.build(story)

    return buffer.getvalue()


@router.post(
    "/report-pdf",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF investigation report"
        }
    }
)
def create_fraud_report(
    file: UploadFile = File(...),
    user=Depends(reviewer_or_admin)
):
    if (
        not file.filename
        or not file.filename.lower().endswith(".csv")
    ):
        raise HTTPException(422, "CSV file required")

    raw = file.file.read(MAX_BYTES + 1)

    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "File exceeds size limit")

    try:
        df = pd.read_csv(
            io.BytesIO(raw),
            encoding="utf-8-sig"
        )
    except (
        ValueError,
        UnicodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError
    ):
        raise HTTPException(422, "Invalid CSV format")

    if not 1 <= len(df) <= MAX_ROWS:
        raise HTTPException(
            422, "CSV must contain 1 to 200 transactions"
        )

    if (
        len(df.columns) != len(FEATURES)
        or set(df.columns) != set(FEATURES)
    ):
        raise HTTPException(
            422, "Required columns: Time, Amount, V1-V28"
        )

    try:
        X = df[FEATURES].apply(
            pd.to_numeric, errors="raise"
        ).astype("float64")
    except (ValueError, TypeError, OverflowError):
        raise HTTPException(422, "Invalid numerical values")

    if not np.isfinite(X.to_numpy()).all():
        raise HTTPException(
            422, "Missing or non-finite values"
        )

    model, threshold = load_model()
    scores = model.predict_proba(X)[:, 1]

    predictions = []

    for index, score in enumerate(scores):
        score = float(score)
        flagged = bool(score >= threshold)

        predictions.append({
            "row_number": index + 1,
            "model_score": score,
            "classification": (
                "FLAGGED" if flagged else "NOT_FLAGGED"
            ),
            "review_recommended": flagged
        })

    pdf_content = generate_pdf(
        predictions, threshold
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            'attachment; filename="fraudshield_report.pdf"',
            "Cache-Control": "no-store"
        }
    )
