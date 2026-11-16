# FraudShield AI — Backend responsibilities & API integration

## System request path
1. Frontend (HTML/CSS/JS) sends authorized `POST /api/v1/predictions` JSON request.
2. FastAPI validates input with Pydantic, decodes bearer JWT and queries PostgreSQL.
3. Risk service returns an **illustrative rule-based risk index** and reasons; `risk_probability` remains `null`.
4. Backend stores the transaction and prediction, creating a **review alert** when flagged.
5. Dashboard and monitoring endpoints query saved records to build live UI charts.
6. Analyst may review alerts. Only `reviewer` and `admin` may change alert status.

## API handoff (to frontend colleague)
- API base URL (local): `http://127.0.0.1:8000/api/v1`
- Swagger: `http://127.0.0.1:8000/docs`
- Auth: JSON `POST /auth/login` returns bearer JWT; send `Authorization: Bearer <token>`.
- Transaction amount uses `amount_minor` **not floating-point currency amounts**. Example INR 1250.50 = `125050` paise.
- All timestamps must have timezone offset, e.g. `2026-11-14T10:30:00+05:30`.
- `features` shape: `{ "new_device": true, "international": false, "tx_24h": 7, "distance_km": 850, "hour": 2 }`.
- `risk_index` is 0-100 **demo index, not model probability**. `model_version` is `demo-rules-v0`; `risk_probability` stays `null`.
- Unauthorized routes return HTTP 401. Invalid Pydantic payloads return 422. Duplicate transaction IDs with changed data return 409.

## Planned (not yet implemented)
- Train supervised XGBoost on properly permissioned labeled data, evaluate time-based held-out metrics (PR-AUC, recall, precision, F1, FPR) and calibrate probabilities where appropriate.
- Train and validate Isolation Forest on appropriate normal-behavior data. Record true anomaly scores separately from fraud probabilities.
- Add SHAP explanations to trained prediction service (avoid sending raw data to third parties).
- Add Alembic migrations, per-tenant scoping, structured audit logs, rate limits, robust RBAC, MFA/SSO, queues, monitoring and secret rotation.
- Add CSV batch ingestion, securely scoped reports, and external API adapters (e.g. verified Stripe test webhooks) only after dedicated security checks.
- The authentication system is a starter; it is not production hardened. Avoid ingesting real financial customer data.
