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
