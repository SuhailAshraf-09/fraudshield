import React, { useState } from 'react';
import { apiService } from '../services/api';
import { PredictionRequest, PredictionResponse } from '../types/api';

interface SandboxProps {
  onPredictionCompleted?: (pred: PredictionResponse) => void;
}

export const FraudDetectionSandbox: React.FC<SandboxProps> = ({ onPredictionCompleted }) => {
  const [transactionId, setTransactionId] = useState(`TX_${Math.floor(1000 + Math.random() * 9000)}`);
  const [amount, setAmount] = useState('1250.00');
  const [currency, setCurrency] = useState('USD');
  const [merchantCategory, setMerchantCategory] = useState('electronics');
  const [newDevice, setNewDevice] = useState(true);
  const [international, setInternational] = useState(false);
  const [tx24h, setTx24h] = useState(6);
  const [distanceKm, setDistanceKm] = useState(850);
  const [hour, setHour] = useState(2);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Preset loaders
  const loadPreset = (type: 'legit' | 'suspicious' | 'critical') => {
    if (type === 'legit') {
      setTransactionId(`TX_LEGIT_${Math.floor(100 + Math.random() * 900)}`);
      setAmount('49.99');
      setCurrency('USD');
      setMerchantCategory('groceries');
      setNewDevice(false);
      setInternational(false);
      setTx24h(1);
      setDistanceKm(5);
      setHour(14);
    } else if (type === 'suspicious') {
      setTransactionId(`TX_SUSP_${Math.floor(100 + Math.random() * 900)}`);
      setAmount('1850.00');
      setCurrency('USD');
      setMerchantCategory('jewelry');
      setNewDevice(true);
      setInternational(true);
      setTx24h(4);
      setDistanceKm(420);
      setHour(23);
    } else if (type === 'critical') {
      setTransactionId(`TX_CRIT_${Math.floor(100 + Math.random() * 900)}`);
      setAmount('12500.00');
      setCurrency('USD');
      setMerchantCategory('crypto_exchange');
      setNewDevice(true);
      setInternational(true);
      setTx24h(14);
      setDistanceKm(4200);
      setHour(3);
    }
  };

  const handleRunEvaluation = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const amountMinor = Math.round(parseFloat(amount || '0') * 100);

    // Build ISO timestamp with local timezone offset
    const now = new Date();
    const offsetMin = -now.getTimezoneOffset();
    const sign = offsetMin >= 0 ? '+' : '-';
    const pad = (n: number) => String(Math.floor(Math.abs(n))).padStart(2, '0');
    const offsetStr = `${sign}${pad(offsetMin / 60)}:${pad(offsetMin % 60)}`;
    const occurredAt = now.toISOString().replace('Z', '') + offsetStr;

    const payload: PredictionRequest = {
      transaction_id: transactionId.trim(),
      amount_minor: amountMinor,
      currency: currency.trim().toUpperCase(),
      occurred_at: occurredAt,
      merchant_category: merchantCategory,
      features: {
        new_device: newDevice,
        international,
        tx_24h: Number(tx24h),
        distance_km: Number(distanceKm),
        hour: Number(hour),
      },
    };

    try {
      const response = await apiService.predict(payload);
      setResult(response);
      if (onPredictionCompleted) {
        onPredictionCompleted(response);
      }
    } catch (err: any) {
      setError(err.message || 'Error executing fraud evaluation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sandbox-container glass-panel">
      <div className="sandbox-header">
        <div>
          <h2 className="sandbox-title">🎯 AI Fraud Prediction Sandbox</h2>
          <p className="sandbox-subtitle">
            Directly test the transaction assessment engine (POST /api/v1/predictions)
          </p>
        </div>

        {/* Preset quick buttons */}
        <div className="presets-group">
          <span className="presets-label">Quick Presets:</span>
          <button type="button" className="preset-pill" onClick={() => loadPreset('legit')}>
            🟢 Normal E-Commerce
          </button>
          <button type="button" className="preset-pill" onClick={() => loadPreset('suspicious')}>
            🟡 Suspicious Travel
          </button>
          <button type="button" className="preset-pill danger" onClick={() => loadPreset('critical')}>
            🔴 Critical Syndicate
          </button>
        </div>
      </div>

      <div className="sandbox-columns">
        {/* Left: Input Form */}
        <form className="sandbox-form" onSubmit={handleRunEvaluation}>
          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">Transaction ID</label>
              <input
                type="text"
                className="form-input"
                value={transactionId}
                onChange={(e) => setTransactionId(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Amount</label>
              <div className="currency-input-wrap">
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                />
                <select
                  className="form-select currency-sel"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="INR">INR (₹)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">Merchant Category</label>
              <select
                className="form-select"
                value={merchantCategory}
                onChange={(e) => setMerchantCategory(e.target.value)}
              >
                <option value="online">Online Retail</option>
                <option value="electronics">Electronics</option>
                <option value="crypto_exchange">Cryptocurrency Exchange</option>
                <option value="jewelry">Luxury / Jewelry</option>
                <option value="travel_airlines">Airlines / Travel</option>
                <option value="groceries">Groceries</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Transaction Velocity (24h count)</label>
              <input
                type="number"
                min="0"
                max="100"
                className="form-input"
                value={tx24h}
                onChange={(e) => setTx24h(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">Distance from Last Location (km)</label>
              <input
                type="number"
                min="0"
                max="40000"
                className="form-input"
                value={distanceKm}
                onChange={(e) => setDistanceKm(Number(e.target.value))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Transaction Hour (0-23)</label>
              <input
                type="number"
                min="0"
                max="23"
                className="form-input"
                value={hour}
                onChange={(e) => setHour(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="form-checkbox-row">
            <label className="form-checkbox-label">
              <input
                type="checkbox"
                checked={newDevice}
                onChange={(e) => setNewDevice(e.target.checked)}
              />
              <span>New / Unrecognized Device Fingerprint</span>
            </label>

            <label className="form-checkbox-label">
              <input
                type="checkbox"
                checked={international}
                onChange={(e) => setInternational(e.target.checked)}
              />
              <span>Cross-Border International IP</span>
            </label>
          </div>

          <button type="submit" className="btn btn-gold run-eval-btn" disabled={loading}>
            {loading ? (
              <span>Analyzing Risk Vectors...</span>
            ) : (
              <>
                <span>Run AI Risk Evaluation</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </>
            )}
          </button>
        </form>

        {/* Right: Real-time Evaluation Result Box */}
        <div className="sandbox-result-box">
          <div className="result-header-row">
            <span className="result-title">Model Evaluation Output</span>
            {result?.demo_only && <span className="demo-tag">DEMO ENGINE</span>}
          </div>

          {error && <div className="result-error-banner">{error}</div>}

          {result ? (
            <div className="result-content-active">
              {/* Score Meter */}
              <div className="risk-score-display">
                <div className="risk-meter-ring">
                  <div
                    className={`meter-fill ${
                      result.risk_tier === 'HIGH'
                        ? 'fill-red'
                        : result.risk_tier === 'MEDIUM'
                        ? 'fill-gold'
                        : 'fill-green'
                    }`}
                    style={{ width: `${result.risk_index}%` }}
                  />
                </div>
                <div className="score-numbers-row">
                  <div>
                    <span className="score-val">{result.risk_index}</span>
                    <span className="score-max">/ 100</span>
                  </div>
                  <div className={`risk-tier-badge tier-${result.risk_tier.toLowerCase()}`}>
                    {result.risk_tier} RISK
                  </div>
                </div>
              </div>

              {/* Status details */}
              <div className="result-meta-grid">
                <div className="meta-item">
                  <span className="meta-lbl">Prediction ID:</span>
                  <span className="meta-val mono">{result.prediction_id}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-lbl">Model Version:</span>
                  <span className="meta-val">{result.model_version}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-lbl">Requires Review:</span>
                  <span className={`meta-val ${result.requires_review ? 'text-red' : 'text-green'}`}>
                    {result.requires_review ? 'YES (Flagged for Review)' : 'NO (Auto-Approved)'}
                  </span>
                </div>
              </div>

              {/* Reasons */}
              <div className="reasons-list-block">
                <div className="reasons-title">Detected Risk Factors & Reasons:</div>
                <ul className="reasons-items">
                  {result.reasons.map((r, i) => (
                    <li key={i} className="reason-item">
                      <span className="bullet-dot" />
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="result-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#555" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
              <p>Configure transaction parameters on the left and click "Run AI Risk Evaluation"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
