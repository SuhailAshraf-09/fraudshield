/**
 * FraudShield AI - TypeScript Definitions
 * Directly aligned with FastAPI app/schemas.py & app/models.py
 */

export type RiskTier = 'LOW' | 'MEDIUM' | 'HIGH';

export interface RiskFeatures {
  new_device: boolean;
  international: boolean;
  tx_24h: number;
  distance_km: number;
  hour: number;
}

export interface PredictionRequest {
  transaction_id: string;
  amount_minor: number;
  currency: string;
  occurred_at: string; // ISO 8601 with timezone, e.g. "2026-11-19T16:00:00+05:30"
  merchant_category?: string;
  features: RiskFeatures;
}

export interface PredictionResponse {
  transaction_id: string;
  prediction_id: string;
  risk_probability?: number | null;
  anomaly_score?: number | null;
  risk_index: number; // 0 to 100
  risk_tier: RiskTier;
  reasons: string[];
  model_version: string;
  requires_review: boolean;
  demo_only: boolean;
}

export interface TransactionItem {
  id: string;
  amount_minor: number;
  currency: string;
  occurred_at: string;
  merchant_category?: string;
  risk_tier?: RiskTier;
  risk_index?: number;
  prediction?: PredictionResponse;
}

export interface AlertItem {
  id: string;
  transaction_id: string;
  status: 'open' | 'in_review' | 'resolved' | 'dismissed';
  priority: 'low' | 'medium' | 'high';
  assigned_user_id?: string | null;
  notes?: string | null;
  amount_display?: string;
  timestamp_display?: string;
}

export interface AlertUpdatePayload {
  status: 'in_review' | 'resolved' | 'dismissed';
  notes?: string;
}

export interface DashboardSummary {
  total_transactions: number;
  flagged_transactions: number;
  open_alerts: number;
  active_users?: number;
  risk_rate_percent?: number;
  period_start?: string | null;
  period_end: string;
  demo_only: boolean;
  note?: string;
}

export interface TrendDataPoint {
  day: string;
  total: number;
  flagged: number;
}

export interface ModelActiveInfo {
  version: string;
  type: string;
  demo_only: boolean;
  trained_at?: string | null;
  artifact_hash?: string | null;
  feature_schema_hash?: string | null;
}

export interface UserPublic {
  id: string;
  email: string;
  role: 'admin' | 'reviewer' | 'analyst' | 'viewer';
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
}

export interface ApiStatus {
  connected: boolean;
  mode: 'live_backend' | 'standalone_demo';
  baseUrl: string;
  latencyMs?: number;
  error?: string;
}
