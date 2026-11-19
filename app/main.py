"""FraudShield AI - FastAPI starter. No live payments, no real fraud model yet."""
import json
import os
from collections import Counter
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Alert, Prediction, Transaction, User
from .risk import assess, MODEL_VERSION
from .schemas import AlertUpdate, LoginRequest, RegisterRequest, PredictionRequest, PredictionResponse, UserPublic
from .security import current_user, hash_password, issue_token, reviewer_or_admin, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Local prototype only. Use Alembic migrations for real deployments.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FraudShield AI Backend", version="0.1.0", lifespan=lifespan,
              description="Python/FastAPI prototype. Fraud outputs are demonstration risk indices, not calibrated probabilities.")
app.add_middleware(CORSMiddleware, allow_origins=list(settings().cors_origins), allow_credentials=False,
                   allow_methods=["GET", "POST", "PATCH"], allow_headers=["Authorization", "Content-Type"])


@app.get("/api/v1/health/live", tags=["Operations"])
def health_live():
    return {"status": "alive"}


@app.get("/api/v1/health/ready", tags=["Operations"])
def health_ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        raise HTTPException(503, "Database unavailable")


@app.post("/api/v1/auth/login", tags=["Authentication"])
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return issue_token(user)


@app.post("/api/v1/auth/register", response_model=UserPublic, tags=["Authentication"])
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Valid email required")
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "User with this email already exists")
    try:
        pw_hash = hash_password(body.password)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    user = User(
        email=email,
        role=body.role if body.role in {"admin", "reviewer", "analyst"} else "analyst",
        password_hash=pw_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@app.get("/api/v1/auth/me", response_model=UserPublic, tags=["Authentication"])
def me(user: User = Depends(current_user)):
    return user


def response_for(prediction: Prediction) -> PredictionResponse:
    return PredictionResponse(transaction_id=prediction.transaction_id, prediction_id=prediction.id,
                              risk_index=prediction.risk_index, risk_tier=prediction.risk_tier,
                              reasons=json.loads(prediction.reasons_json), model_version=prediction.model_version,
                              requires_review=prediction.requires_review, demo_only=True)


@app.post("/api/v1/predictions", response_model=PredictionResponse, tags=["Predictions"])
def predict(body: PredictionRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    stored = db.get(Transaction, body.transaction_id)
    body_features = body.features.model_dump_json()
    if stored:
        if (stored.amount_minor != body.amount_minor or stored.currency != body.currency or
            stored.features_json != body_features or stored.occurred_at.replace(tzinfo=timezone.utc) != body.occurred_at.astimezone(timezone.utc)):
            raise HTTPException(status.HTTP_409_CONFLICT, "Transaction ID already used for different data")
        return response_for(stored.prediction)

    risk_index, tier, reasons = assess(body)
    tx = Transaction(id=body.transaction_id, amount_minor=body.amount_minor, currency=body.currency,
                     occurred_at=body.occurred_at.astimezone(timezone.utc), merchant_category=body.merchant_category,
                     features_json=body_features)
    prediction = Prediction(transaction_id=tx.id, risk_index=risk_index, risk_tier=tier,
                            reasons_json=json.dumps(reasons), model_version=MODEL_VERSION,
                            requires_review=tier in {"MEDIUM", "HIGH"})
    db.add(tx)
    db.add(prediction)
    if prediction.requires_review:
        db.add(Alert(transaction_id=tx.id, status="open", priority=tier.lower()))
    db.commit()
    db.refresh(prediction)
    return response_for(prediction)


@app.get("/api/v1/transactions", tags=["Transactions"])
def transactions(limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0),
                 db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(Transaction).order_by(Transaction.created_at.desc()).offset(offset).limit(limit)).all()
    return [{"id": x.id, "amount_minor": x.amount_minor, "currency": x.currency,
             "occurred_at": x.occurred_at, "merchant_category": x.merchant_category,
             "risk_tier": x.prediction.risk_tier if x.prediction else None,
             "risk_index": x.prediction.risk_index if x.prediction else None} for x in rows]


@app.get("/api/v1/transactions/{transaction_id}", tags=["Transactions"])
def transaction_detail(transaction_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    x = db.get(Transaction, transaction_id)
    if not x:
        raise HTTPException(404, "Transaction not found")
    return {"id": x.id, "amount_minor": x.amount_minor, "currency": x.currency,
            "occurred_at": x.occurred_at, "merchant_category": x.merchant_category,
            "prediction": response_for(x.prediction) if x.prediction else None}


@app.get("/api/v1/dashboard/summary", tags=["Analytics"])
def dashboard_summary(db: Session = Depends(get_db), user: User = Depends(current_user)):
    total = db.scalar(select(func.count(Transaction.id))) or 0
    flagged = db.scalar(select(func.count(Prediction.id)).where(Prediction.requires_review.is_(True))) or 0
    open_alerts = db.scalar(select(func.count(Alert.id)).where(Alert.status.in_(["open", "in_review"]))) or 0
    now = datetime.now(timezone.utc)
    return {"total_transactions": total, "flagged_transactions": flagged, "open_alerts": open_alerts,
            "period_start": None, "period_end": now.isoformat(), "demo_only": True,
            "note": "All counts reflect locally stored demo assessments; not confirmed fraud."}


@app.get("/api/v1/analytics/trends", tags=["Analytics"])
def trends(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db), user: User = Depends(current_user)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    txs = db.scalars(select(Transaction).where(Transaction.created_at >= since)).all()
    totals = Counter(x.created_at.date().isoformat() for x in txs)
    flagged = Counter(x.created_at.date().isoformat() for x in txs if x.prediction and x.prediction.requires_review)
    today = datetime.now(timezone.utc).date()
    return [{"day": (today - timedelta(days=i)).isoformat(), "total": totals[(today - timedelta(days=i)).isoformat()],
             "flagged": flagged[(today - timedelta(days=i)).isoformat()]} for i in reversed(range(days))]


@app.get("/api/v1/alerts", tags=["Investigations"])
def alerts(limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(limit)).all()
    return [{"id": a.id, "transaction_id": a.transaction_id, "status": a.status,
             "priority": a.priority, "assigned_user_id": a.assigned_user_id, "notes": a.notes} for a in rows]


@app.get("/api/v1/alerts/{alert_id}", tags=["Investigations"])
def alert_detail(alert_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    a = db.get(Alert, alert_id)
    if not a:
        raise HTTPException(404, "Alert not found")
    return {"id": a.id, "transaction_id": a.transaction_id, "status": a.status,
            "priority": a.priority, "assigned_user_id": a.assigned_user_id, "notes": a.notes}


@app.patch("/api/v1/alerts/{alert_id}", tags=["Investigations"])
def alert_update(alert_id: str, body: AlertUpdate, db: Session = Depends(get_db), user: User = Depends(reviewer_or_admin)):
    a = db.get(Alert, alert_id)
    if not a:
        raise HTTPException(404, "Alert not found")
    a.status = body.status
    a.notes = body.notes
    db.commit()
    return {"id": a.id, "transaction_id": a.transaction_id, "status": a.status, "priority": a.priority,
            "notes": a.notes}


@app.get("/api/v1/models/active", tags=["Models"])
def model_active(user: User = Depends(current_user)):
    return {"version": MODEL_VERSION, "type": "transparent rules", "demo_only": True,
            "trained_at": None, "artifact_hash": None, "feature_schema_hash": None}


@app.get("/api/v1/models/metrics", tags=["Models"])
def model_metrics(user: User = Depends(current_user)):
    return {"status": "not_evaluated", "precision": None, "recall": None, "pr_auc": None,
            "f1_score": None, "false_positive_rate": None, "reason": "A validated supervised model has not been trained yet"}


# Serve Frontend Web Application
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

