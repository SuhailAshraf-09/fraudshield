from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    role: str


class RiskFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    new_device: bool = False
    international: bool = False
    tx_24h: int = Field(1, ge=0, le=1000)
    distance_km: float = Field(0, ge=0, le=40075)
    hour: int = Field(12, ge=0, le=23)


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transaction_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    amount_minor: int = Field(ge=0, le=10**14)
    currency: str = Field(min_length=3, max_length=3)
    occurred_at: datetime
    merchant_category: str | None = Field(None, max_length=100)
    features: RiskFeatures = Field(default_factory=RiskFeatures)

    @field_validator("currency")
    @classmethod
    def currency_code(cls, value: str) -> str:
        code = value.upper()
        if not code.isascii() or not code.isalpha():
            raise ValueError("currency must be a 3-letter ISO-style code")
        return code

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must include a UTC offset, e.g. +00:00")
        return value


class PredictionResponse(BaseModel):
    transaction_id: str
    prediction_id: str
    risk_probability: float | None = None
    anomaly_score: float | None = None
    risk_index: float = Field(ge=0, le=100)
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    reasons: list[str]
    model_version: str
    requires_review: bool
    demo_only: bool = True


class AlertUpdate(BaseModel):
    status: Literal["in_review", "resolved", "dismissed"]
    notes: str | None = Field(None, max_length=10000)
