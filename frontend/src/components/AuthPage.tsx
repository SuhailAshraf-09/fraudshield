import React, { useState } from 'react';
import { apiService } from '../services/api';
import { UserPublic } from '../types/api';

interface AuthPageProps {
  initialMode?: 'login' | 'register';
  onAuthSuccess: (user: UserPublic) => void;
  onBackToHome: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({
  initialMode = 'login',
  onAuthSuccess,
  onBackToHome,
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);

  // Login form state
  const [loginEmail, setLoginEmail] = useState('admin@fraudshield.ai');
  const [loginPassword, setLoginPassword] = useState('AdminSecret2026!');
  const [rememberMe, setRememberMe] = useState(true);

  // Register form state
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regRole, setRegRole] = useState<'analyst' | 'reviewer' | 'admin'>('analyst');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [regTerms, setRegTerms] = useState(false);

  // Shared state
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle Login Submit
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiService.login(loginEmail.trim(), loginPassword);
      const user = apiService.getStoredUser() || {
        id: 'usr_active',
        email: loginEmail.trim(),
        role: 'admin',
      };
      onAuthSuccess(user);
    } catch (err: any) {
      setError(err.message || 'Invalid email or password. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Handle Register Submit
  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (regPassword !== regConfirmPassword) {
      setError('Passwords do not match. Please re-enter.');
      setLoading(false);
      return;
    }

    if (regPassword.length < 12) {
      setError('Password must be at least 12 characters long according to security policy.');
      setLoading(false);
      return;
    }

    if (!regTerms) {
      setError('Please agree to the Security & Compliance Terms to continue.');
      setLoading(false);
      return;
    }

    try {
      const newUser = await apiService.register({
        email: regEmail.trim(),
        password: regPassword,
        role: regRole,
        full_name: regFullName.trim(),
      });

      // Automatically sign in the newly registered user
      await apiService.login(regEmail.trim(), regPassword);
      onAuthSuccess(newUser);
    } catch (err: any) {
      setError(err.message || 'Registration failed. An account with this email may already exist.');
    } finally {
      setLoading(false);
    }
  };

  // Quick Demo Autofill
  const autofillDemoAdmin = () => {
    setLoginEmail('admin@fraudshield.ai');
    setLoginPassword('AdminSecret2026!');
    setError(null);
  };

  const autofillDemoAnalyst = () => {
    setLoginEmail('analyst@fraudshield.ai');
    setLoginPassword('AnalystPass2026!');
    setError(null);
  };

  return (
    <div className="auth-page-wrapper">
      {/* Background Cyber Glow & Ribbons */}
      <div className="cyber-bg-glow" />
      <div className="cyber-lines-overlay" />

      {/* Top back to home link */}
      <div className="auth-top-bar">
        <button className="back-home-btn" onClick={onBackToHome}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to FraudShield AI
        </button>
      </div>

      <div className="auth-container">
        {/* Brand Banner on top of card */}
        <div className="auth-brand-center">
          <div className="auth-shield-logo-wrap">
            <svg viewBox="0 0 44 48" className="auth-logo-svg" fill="none">
              <path
                d="M22 2 L40 10 C40 30 22 46 22 46 C22 46 4 30 4 10 Z"
                fill="#200407"
                stroke="url(#authShieldGold)"
                strokeWidth="2.8"
              />
              <path
                d="M22 6 L36 12 C36 28 22 41 22 41 C22 41 8 28 8 12 Z"
                stroke="#FF385C"
                strokeWidth="1.2"
                opacity="0.8"
              />
              <g transform="translate(22, 23) scale(0.38)" stroke="#FFD166" strokeWidth="3" strokeLinecap="round">
                <path d="M-6 10 C -6 -4, 6 -4, 6 10" />
                <path d="M0 12 L0 2" />
                <path d="M-13 14 C -13 -10, 13 -10, 13 14" />
                <path d="M-20 18 C -20 -16, 20 -16, 20 18" />
                <path d="M-26 22 C -26 -22, 26 -22, 26 22" />
              </g>
              <defs>
                <linearGradient id="authShieldGold" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFE066" />
                  <stop offset="100%" stopColor="#D97706" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h2 className="auth-main-heading">
            FraudShield <span className="gold-accent">AI</span>
          </h2>
          <p className="auth-sub-heading">
            {mode === 'login'
              ? 'Sign in to access your real-time fraud monitoring dashboard'
              : 'Create an enterprise account to secure transactions with AI'}
          </p>
        </div>

        {/* Main Card */}
        <div className="auth-glass-card">
          {/* Tab Switcher */}
          <div className="auth-tab-switch">
            <button
              type="button"
              className={`auth-tab-btn ${mode === 'login' ? 'active' : ''}`}
              onClick={() => {
                setMode('login');
                setError(null);
              }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`auth-tab-btn ${mode === 'register' ? 'active' : ''}`}
              onClick={() => {
                setMode('register');
                setError(null);
              }}
            >
              Register Account
            </button>
          </div>

          {error && (
            <div className="auth-error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* ================= SIGN IN FORM ================= */}
          {mode === 'login' && (
            <form onSubmit={handleLoginSubmit} className="auth-form-body">
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <div className="input-with-icon">
                  <span className="input-icon">✉️</span>
                  <input
                    type="email"
                    className="form-input icon-padded"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="name@organization.com"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <div className="label-with-action">
                  <label className="form-label">Password</label>
                  <button
                    type="button"
                    className="forgot-link"
                    onClick={() => alert('Password reset link sent to registered email.')}
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="input-with-icon">
                  <span className="input-icon">🔒</span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-input icon-padded"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••••••"
                    required
                  />
                  <button
                    type="button"
                    className="eye-toggle-btn"
                    onClick={() => setShowPassword(!showPassword)}
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? '👁️' : '🙈'}
                  </button>
                </div>
              </div>

              <div className="form-options-row">
                <label className="form-checkbox-label">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Keep me signed in for 30 days</span>
                </label>
              </div>

              <button type="submit" className="btn btn-gold auth-submit-btn" disabled={loading}>
                {loading ? (
                  <span>Authenticating Securely...</span>
                ) : (
                  <>
                    <span>Sign In to Dashboard</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </>
                )}
              </button>

              {/* Demo quick links */}
              <div className="auth-quick-demo">
                <span className="demo-label">Quick Demo Logins:</span>
                <div className="demo-buttons-row">
                  <button type="button" className="demo-fill-btn" onClick={autofillDemoAdmin}>
                    🛡️ Admin (Full Access)
                  </button>
                  <button type="button" className="demo-fill-btn" onClick={autofillDemoAnalyst}>
                    📊 Risk Analyst
                  </button>
                </div>
              </div>

              <div className="auth-switch-footer">
                <span>Don't have an account yet?</span>
                <button
                  type="button"
                  className="link-switch"
                  onClick={() => {
                    setMode('register');
                    setError(null);
                  }}
                >
                  Register here →
                </button>
              </div>
            </form>
          )}

          {/* ================= REGISTER FORM ================= */}
          {mode === 'register' && (
            <form onSubmit={handleRegisterSubmit} className="auth-form-body">
              <div className="form-group">
                <label className="form-label">Full Name / Organization</label>
                <div className="input-with-icon">
                  <span className="input-icon">👤</span>
                  <input
                    type="text"
                    className="form-input icon-padded"
                    value={regFullName}
                    onChange={(e) => setRegFullName(e.target.value)}
                    placeholder="Jane Doe (Fintech Corp)"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Corporate Email Address</label>
                <div className="input-with-icon">
                  <span className="input-icon">✉️</span>
                  <input
                    type="email"
                    className="form-input icon-padded"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="jane@fintech.com"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Security Role</label>
                <select
                  className="form-select"
                  value={regRole}
                  onChange={(e) => setRegRole(e.target.value as any)}
                >
                  <option value="analyst">Risk Analyst (Assessments & Queries)</option>
                  <option value="reviewer">Fraud Investigator / Reviewer (Alert Resolution)</option>
                  <option value="admin">Security Administrator (Full System Operations)</option>
                </select>
              </div>

              <div className="form-grid-2">
                <div className="form-group">
                  <label className="form-label">Password (12+ chars)</label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-input"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Min. 12 characters"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Confirm Password</label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-input"
                    value={regConfirmPassword}
                    onChange={(e) => setRegConfirmPassword(e.target.value)}
                    placeholder="Re-enter password"
                    required
                  />
                </div>
              </div>

              <div className="form-options-row">
                <label className="form-checkbox-label">
                  <input
                    type="checkbox"
                    checked={regTerms}
                    onChange={(e) => setRegTerms(e.target.checked)}
                    required
                  />
                  <span>
                    I accept the <strong>PCI-DSS & SOC2 Security Policy</strong> and authorize real-time transaction telemetry.
                  </span>
                </label>
              </div>

              <button type="submit" className="btn btn-gold auth-submit-btn" disabled={loading}>
                {loading ? (
                  <span>Registering Account & Issuing Keys...</span>
                ) : (
                  <>
                    <span>Create Account & Unlock Dashboard</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </>
                )}
              </button>

              <div className="auth-switch-footer">
                <span>Already have a FraudShield account?</span>
                <button
                  type="button"
                  className="link-switch"
                  onClick={() => {
                    setMode('login');
                    setError(null);
                  }}
                >
                  Sign In here →
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
