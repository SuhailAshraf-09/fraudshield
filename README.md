# FraudShield AI — Python FastAPI Backend (Starter)

An **actual runnable backend scaffold** for the approved FraudShield AI project and proposed API specification. Includes protected API routes, database tables, illustrative risk-index scoring, alerts, dashboard summaries and documentation; **it does not contain a trained/validated fraud classifier**.

## Quick start (Windows PowerShell)

```powershell
cd FraudShield_AI_Backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# EDIT .env and replace JWT_SECRET with a unique random 32+ character secret!
python -m app.create_admin
uvicorn app.main:app --reload
```

Mac/Linux: `python3 -m venv .venv`, `source .venv/bin/activate`, `cp .env.example .env`, then the same commands.

Open http://127.0.0.1:8000/docs, use `/api/v1/auth/login`, click **Authorize** and paste the access token; test `/api/v1/predictions`, `/api/v1/dashboard/summary`, `/api/v1/alerts`.

`python -c "import secrets; print(secrets.token_urlsafe(48))"` generates a suitable random JWT secret. The example placeholder is intentionally rejected by the auth layer.

**Docker with local PostgreSQL:** Set `POSTGRES_PASSWORD` and `JWT_SECRET` in `.env`, then run `docker compose up --build` (requires Docker Desktop or Docker Engine). This is intended only for local development.

## JSON example: `POST /api/v1/predictions`

```json
{
  "transaction_id": "DEMO_001",
  "amount_minor": 8500000,
  "currency": "INR",
  "occurred_at": "2026-11-14T10:30:00+05:30",
  "merchant_category": "online",
  "features": {
    "new_device": true,
    "international": true,
    "tx_24h": 10,
    "distance_km": 900,
    "hour": 2
  }
}
```

The response returns a **demo risk index and tier**, explanation reasons, prediction ID and model version, not a fraud probability.

## Team handoff

- You: Python, model development, risk logic, FastAPI endpoints, validation, testing.
- Colleague: remaining frontend and PostgreSQL schema; align migrations with `app/models.py` and the documented JSON contract.
- Shared: auth/security design, endpoint integration, responsive UI, database migrations and deployment.

## Data storage and production cautions

SQLite is enabled for **local development only**. For PostgreSQL, use `DATABASE_URL=postgresql+psycopg://...` and add migrations before production. Docker Compose provides a local PostgreSQL example but is **not a production deployment configuration**. Do not commit `.env`, use real bank credentials, store full PAN/CVV, or claim demo risk scores are a tested fraud model.

## Tests

```bash
pytest -q
```

See `docs/BACKEND_PLAN.md` for the entire request path, roles, feature contract and planned ML/external integration work.

---

## Backend Development Progress - November 19, 2026

> This section documents the latest backend development.
> The original starter documentation above is preserved
> as historical project documentation.

### Technology Stack

- Python and FastAPI
- PostgreSQL and SQLAlchemy
- JWT authentication and role-based access control
- NumPy, Pandas, and Scikit-learn
- Random Forest fraud detection
- XGBoost, Logistic Regression, and Isolation Forest experiments
- Docker Desktop and WSL 2
- PDF investigation reports using ReportLab

### Implemented Backend Features

- JWT authentication and protected API endpoints
- Admin and reviewer authorization for prediction operations
- Random Forest transaction fraud classification
- CSV batch prediction API
- PDF fraud investigation report generation
- PostgreSQL prediction storage
- High-risk fraud alert generation
- Dashboard, transaction, and alert APIs
- Security regression testing
- Dockerized FastAPI application

### Random Forest Final Test Evaluation

The existing trained model was evaluated on held-out test data.

| Metric | Result |
|---|---:|
| Test transactions | 56,746 |
| Actual fraud cases | 95 |
| Precision | 88.89% |
| Recall | 75.79% |
| F1 Score | 81.82% |
| Average Precision (PR-AUC summary) | 79.87% |
| ROC-AUC | 95.61% |
| True Positives | 72 |
| False Positives | 9 |
| True Negatives | 56,642 |
| False Negatives | 23 |

The selected Random Forest decision threshold was
approximately 0.310531.

These are development evaluation results, not production
performance guarantees. The model is not production-certified.

### Security Verification

- Legacy prediction API reviewer/admin RBAC test passed
- Admin and reviewer authorization checks passed
- Viewer write access correctly denied
- JWT security baseline passed
- Docker API unauthenticated access tests passed (8/8)
- No unauthorized database writes in these tests

These tests do not replace a complete production security audit.

### Docker Integration

Successfully verified:

- Docker image build
- Trained Random Forest model loading in Docker
- FastAPI route registration
- Container HTTP health endpoint
- Isolated PostgreSQL 17 container connectivity
- Required PostgreSQL tables
- JWT-protected endpoints
- Temporary test container and network cleanup

Docker image:

`fraudshield-ai-backend:phase10`

Build command:

```powershell
docker build -t fraudshield-ai-backend:phase10 .
```

The Docker tests used an isolated PostgreSQL instance.
The existing compose.yaml has not yet been validated for
the updated application configuration. Do not use it for
production deployment without further configuration.

### Project Status

Backend development and major integration tests are complete
for the current development milestone.

Remaining work includes production hardening, deployment
configuration review, further regression testing, and
frontend integration.

### Important Notes

- This is a fraud detection demonstration and development project.
- Model scores are not calibrated fraud probabilities.
- High-risk predictions require human review.
- Local datasets, secrets, database files, and test reports
  are excluded from GitHub and Docker build contexts.
