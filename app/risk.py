"""Transparent DEMO risk index, NOT a trained fraud classifier or probability."""
from .schemas import PredictionRequest


MODEL_VERSION = "demo-rules-v0"


def assess(transaction: PredictionRequest) -> tuple[float, str, list[str]]:
    f = transaction.features
    score = 5.0
    reasons: list[str] = []
    if f.new_device:
        score += 17
        reasons.append("Transaction from a new device")
    if f.international:
        score += 22
        reasons.append("Cross-border transaction")
    if f.tx_24h >= 6:
        score += min(25, (f.tx_24h - 5) * 5)
        reasons.append("Elevated 24-hour transaction count")
    if f.distance_km >= 500:
        score += 18
        reasons.append("Large distance from reference location")
    if f.hour <= 4:
        score += 12
        reasons.append("Unusual transaction hour")
    score = min(100.0, score)
    tier = "HIGH" if score >= 65 else "MEDIUM" if score >= 35 else "LOW"
    if not reasons:
        reasons.append("No configured demonstration risk indicators triggered")
    return score, tier, reasons
