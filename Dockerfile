FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /srv/app

# Install FastAPI, PostgreSQL, ML and PDF dependencies
COPY requirements.txt ./requirements.txt

RUN python -m pip install --no-cache-dir -r requirements.txt

# Create a non-root application user
RUN useradd --system --uid 10001 --create-home apiuser

# Copy backend application
COPY --chown=10001:10001 app/ ./app/

# Copy trusted trained Random Forest model
COPY --chown=10001:10001 ml_models/random_forest_v1.joblib ./ml_models/random_forest_v1.joblib
COPY --chown=10001:10001 ml_models/random_forest_v1_metrics.json ./ml_models/random_forest_v1_metrics.json

USER apiuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
