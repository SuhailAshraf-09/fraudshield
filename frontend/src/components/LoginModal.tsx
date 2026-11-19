import React, { useState } from 'react';
import { apiService } from '../services/api';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (email: string) => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [email, setEmail] = useState('admin@fraudshield.ai');
  const [password, setPassword] = useState('AdminSecret2026!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiService.login(email, password);
      onLoginSuccess(email);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay open">
      <div className="modal-box auth-modal">
        <div className="modal-header">
          <div className="auth-brand-head">
            <span className="auth-shield-icon">🛡️</span>
            <h3>FraudShield AI Sign In</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <p className="auth-explainer">
            Authenticate to access live fraud evaluation endpoints and admin operations.
          </p>

          {error && <div className="result-error-banner">{error}</div>}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@fraudshield.ai"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <div className="auth-btn-row">
            <button type="submit" className="btn btn-gold w-full" disabled={loading}>
              {loading ? 'Authenticating with Backend...' : 'Sign In as Admin'}
            </button>
          </div>

          <div className="demo-credentials-note">
            <span>💡 Tip:</span> If local backend is connected, uses <code>/api/v1/auth/login</code>. In demo mode, generates simulated session token.
          </div>
        </form>
      </div>
    </div>
  );
};
