import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { Sidebar, DashboardTab } from './components/Sidebar';
import { DashboardOverview } from './components/DashboardOverview';
import { FraudDetectionSandbox } from './components/FraudDetectionSandbox';
import { TransactionsTable } from './components/TransactionsTable';
import { AlertsManager } from './components/AlertsManager';
import { LoginModal } from './components/LoginModal';
import { BackendSettingsModal } from './components/BackendSettingsModal';
import { apiService } from './services/api';
import {
  AlertItem,
  AlertUpdatePayload,
  ApiStatus,
  DashboardSummary,
  PredictionResponse,
  TransactionItem,
  TrendDataPoint,
} from './types/api';

export type ViewMode = 'showcase' | 'landing' | 'dashboard';

export const App: React.FC = () => {
  // View mode switcher: showcase (both landing & dashboard as in user image), landing only, dashboard only
  const [viewMode, setViewMode] = useState<ViewMode>('showcase');
  const [activeTab, setActiveTab] = useState<DashboardTab>('dashboard');

  // Backend state
  const [apiStatus, setApiStatus] = useState<ApiStatus>({
    connected: false,
    mode: 'standalone_demo',
    baseUrl: apiService.getBaseUrl(),
  });

  // Data states
  const [summary, setSummary] = useState<DashboardSummary>({
    total_transactions: 12480,
    flagged_transactions: 128,
    open_alerts: 3,
    active_users: 2540,
    risk_rate_percent: 1.03,
    period_end: new Date().toISOString(),
    demo_only: true,
  });

  const [trends, setTrends] = useState<TrendDataPoint[]>([]);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  // Modals & Notifications
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<string>('Admin');
  const [liveStreamActive, setLiveStreamActive] = useState(true);
  const [toasts, setToasts] = useState<Array<{ id: string; title: string; desc: string; highRisk?: boolean }>>([]);

  // Fetch initial data
  const loadData = async () => {
    const status = await apiService.checkHealth();
    setApiStatus(status);

    const [summaryData, trendsData, txData, alertsData] = await Promise.all([
      apiService.getDashboardSummary(),
      apiService.getTrends(7),
      apiService.getTransactions(25),
      apiService.getAlerts(),
    ]);

    setSummary(summaryData);
    setTrends(trendsData);
    setTransactions(txData);
    setAlerts(alertsData);
  };

  useEffect(() => {
    loadData();
  }, []);

  // Show Toast
  const addToast = (title: string, desc: string, highRisk = false) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev.slice(-3), { id, title, desc, highRisk }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  };

  // Live Transaction Simulation Stream
  useEffect(() => {
    if (!liveStreamActive) return;

    const interval = setInterval(() => {
      const isRisk = Math.random() < 0.25;
      const amount = Math.floor(20 + Math.random() * 4500);
      const newTx: TransactionItem = {
        id: `TX_${Math.floor(1000 + Math.random() * 9000)}_${Math.random() < 0.5 ? 'US' : 'EU'}`,
        amount_minor: amount * 100,
        currency: 'USD',
        occurred_at: new Date().toISOString(),
        merchant_category: isRisk ? 'crypto_exchange' : 'e_commerce',
        risk_tier: isRisk ? 'HIGH' : 'LOW',
        risk_index: isRisk ? Math.floor(75 + Math.random() * 24) : Math.floor(5 + Math.random() * 25),
      };

      setTransactions((prev) => [newTx, ...prev.slice(0, 30)]);
      setSummary((prev) => ({
        ...prev,
        total_transactions: prev.total_transactions + 1,
        flagged_transactions: isRisk ? prev.flagged_transactions + 1 : prev.flagged_transactions,
      }));

      if (isRisk) {
        addToast(
          '🚨 Critical Fraud Alert Triggered!',
          `Transaction ${newTx.id} ($${amount.toLocaleString()}) flagged with ${newTx.risk_index}% risk index!`,
          true
        );
      }
    }, 9000);

    return () => clearInterval(interval);
  }, [liveStreamActive]);

  // Handle alert update
  const handleUpdateAlert = async (id: string, payload: AlertUpdatePayload) => {
    await apiService.updateAlert(id, payload);
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: payload.status, notes: payload.notes || a.notes } : a))
    );
    addToast('Status Updated', `Alert ${id} marked as ${payload.status}`);
  };

  // When prediction is made in sandbox
  const handlePredictionDone = (pred: PredictionResponse) => {
    addToast(
      `${pred.risk_tier} RISK Evaluated`,
      `Score ${pred.risk_index}/100: ${pred.reasons[0] || 'Evaluated'}`,
      pred.risk_tier === 'HIGH'
    );
  };

  return (
    <div className="fraudshield-app-root">
      {/* Background Cyber Accents */}
      <div className="cyber-bg-glow" />
      <div className="cyber-lines-overlay" />

      {/* Top Bar Switcher: Toggle between Showcase / Landing / Dashboard */}
      <div className="view-switcher-bar">
        <div className="view-switcher-pill">
          <button
            className={`view-btn ${viewMode === 'showcase' ? 'active' : ''}`}
            onClick={() => setViewMode('showcase')}
            title="Shows both Landing Page and Admin Dashboard simultaneously as in design mockup"
          >
            Full Showcase (Image Match)
          </button>
          <button
            className={`view-btn ${viewMode === 'landing' ? 'active' : ''}`}
            onClick={() => setViewMode('landing')}
          >
            Landing Page
          </button>
          <button
            className={`view-btn ${viewMode === 'dashboard' ? 'active' : ''}`}
            onClick={() => setViewMode('dashboard')}
          >
            Dashboard
          </button>
        </div>

        {/* Backend Connectivity Status */}
        <div
          className="backend-pill-indicator"
          style={{ cursor: 'pointer' }}
          onClick={() => setIsSettingsOpen(true)}
          title="Click to configure FastAPI connection"
        >
          <span className={`status-dot ${apiStatus.connected ? 'online' : 'demo'}`} />
          <span>
            {apiStatus.connected ? `FastAPI: Connected (${apiStatus.latencyMs}ms)` : 'Backend: Standalone Demo'}
          </span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </div>
      </div>

      {/* SECTION 1: LANDING PAGE & HERO (Shown in 'showcase' or 'landing') */}
      {(viewMode === 'showcase' || viewMode === 'landing') && (
        <div className="landing-wrapper">
          <Header
            onSignInClick={() => setIsLoginOpen(true)}
            onGetStartedClick={() => {
              setViewMode('dashboard');
              setActiveTab('fraud_detection');
            }}
          />
          <Hero
            onExplorePlatform={() => {
              setViewMode('dashboard');
              setActiveTab('dashboard');
            }}
            onWatchDemo={() => {
              setViewMode('dashboard');
              setActiveTab('fraud_detection');
            }}
          />
        </div>
      )}

      {/* SECTION 2: ADMIN & OPERATIONS DASHBOARD (Shown in 'showcase' or 'dashboard') */}
      {(viewMode === 'showcase' || viewMode === 'dashboard') && (
        <section className="dashboard-section-wrapper" id="dashboard">
          {/* Subtle separator glow for showcase view */}
          {viewMode === 'showcase' && <div className="showcase-section-divider" />}

          <div className="dashboard-layout-container">
            {/* Left Sidebar */}
            <Sidebar
              activeTab={activeTab}
              onTabChange={(tab) => {
                if (tab === 'settings') {
                  setIsSettingsOpen(true);
                } else {
                  setActiveTab(tab);
                }
              }}
              openAlertsCount={alerts.filter((a) => a.status === 'open').length}
              onLogout={() => {
                apiService.setToken(null);
                setCurrentUser('Guest');
                addToast('Logged Out', 'You have been logged out of the session');
              }}
            />

            {/* Dashboard Main View Area */}
            <main className="dashboard-main-area">
              {/* Dashboard Top Header Bar (Search, Alerts, Admin profile) */}
              <header className="dashboard-top-navbar">
                <div className="top-nav-left">
                  <button className="hamburger-btn" aria-label="Menu">
                    <span className="ham-line" />
                    <span className="ham-line" />
                    <span className="ham-line" />
                  </button>

                  <div className="global-search-bar">
                    <span className="search-icon">🔍</span>
                    <input
                      type="text"
                      placeholder="Search transactions, users..."
                      className="search-input-field"
                    />
                  </div>
                </div>

                <div className="top-nav-right">
                  {/* Live Stream Toggle */}
                  <button
                    className={`live-pulse-btn ${liveStreamActive ? 'active' : ''}`}
                    onClick={() => setLiveStreamActive(!liveStreamActive)}
                    title="Toggle real-time simulated transaction stream"
                  >
                    <span className="pulse-dot-indicator" />
                    <span>Live Stream {liveStreamActive ? 'ON' : 'PAUSED'}</span>
                  </button>

                  {/* Notification Bell with Badge */}
                  <div className="notification-bell-wrap" onClick={() => setActiveTab('alerts')}>
                    <span className="bell-icon">🔔</span>
                    {alerts.filter((a) => a.status === 'open').length > 0 && (
                      <span className="bell-badge">
                        {alerts.filter((a) => a.status === 'open').length}
                      </span>
                    )}
                  </div>

                  {/* Admin User Profile */}
                  <div className="user-profile-pill" onClick={() => setIsLoginOpen(true)}>
                    <div className="user-avatar-circle">
                      <img
                        src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&auto=format&fit=crop&q=80"
                        alt="Admin"
                        onError={(e) => {
                          // Fallback if image blocked
                          (e.target as HTMLElement).style.display = 'none';
                        }}
                      />
                      <span className="avatar-fallback">👤</span>
                    </div>
                    <span className="user-name">{currentUser}</span>
                    <span className="dropdown-caret">˅</span>
                  </div>
                </div>
              </header>

              {/* Dynamic View Content based on Sidebar Selection */}
              {activeTab === 'dashboard' && (
                <DashboardOverview
                  summary={summary}
                  trends={trends}
                  alerts={alerts}
                  onViewAllAlerts={() => setActiveTab('alerts')}
                  onUpgradeClick={() => {
                    addToast('Enterprise Plan', 'Contact sales@fraudshield.ai for custom high-volume quotas');
                  }}
                  onInvestigateAlert={() => setActiveTab('alerts')}
                />
              )}

              {activeTab === 'fraud_detection' && (
                <FraudDetectionSandbox onPredictionCompleted={handlePredictionDone} />
              )}

              {activeTab === 'transactions' && (
                <TransactionsTable transactions={transactions} />
              )}

              {activeTab === 'alerts' && (
                <AlertsManager
                  alerts={alerts}
                  onUpdateAlert={handleUpdateAlert}
                  onRefreshAlerts={loadData}
                />
              )}

              {activeTab === 'analytics' && (
                <div className="analytics-full-view glass-panel">
                  <h2 className="table-title">📊 Advanced Machine Learning Models & Metrics</h2>
                  <p className="table-subtitle">Ensemble scoring metrics, ROC-AUC, Precision/Recall, and Feature Drift</p>
                  <div style={{ marginTop: '20px' }}>
                    <DashboardOverview
                      summary={summary}
                      trends={trends}
                      alerts={alerts}
                      onViewAllAlerts={() => setActiveTab('alerts')}
                      onUpgradeClick={() => {}}
                      onInvestigateAlert={() => {}}
                    />
                  </div>
                </div>
              )}

              {activeTab === 'reports' && (
                <div className="reports-view glass-panel">
                  <h2 className="table-title">📑 Compliance & Fraud Audit Reports</h2>
                  <p className="table-subtitle">Download SAR (Suspicious Activity Reports), PCI-DSS logs, and monthly risk retrospectives</p>
                  <div style={{ marginTop: '24px', display: 'flex', gap: '15px' }}>
                    <button className="btn btn-gold" onClick={() => addToast('Export Generated', 'Exported fraudshield_audit_2026.csv')}>
                      Download Monthly CSV
                    </button>
                    <button className="btn btn-outline" onClick={() => addToast('PDF Report', 'Generated executive summary PDF')}>
                      Export Executive PDF
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'users' && (
                <div className="users-view glass-panel">
                  <h2 className="table-title">👥 Security Operations & Reviewer Team</h2>
                  <p className="table-subtitle">Assign fraud alert queues, reviewer permissions, and MFA policies</p>
                  <div style={{ marginTop: '16px' }}>
                    <div className="user-row-pill">
                      <span>👤 admin@fraudshield.ai</span>
                      <span className="risk-badge badge-low">Super Admin</span>
                    </div>
                  </div>
                </div>
              )}
            </main>
          </div>
        </section>
      )}

      {/* Modals & Popups */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={(email) => {
          setCurrentUser(email.split('@')[0]);
          addToast('Welcome Back', `Authenticated as ${email}`);
        }}
      />

      <BackendSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        status={apiStatus}
        onStatusUpdated={(s) => {
          setApiStatus(s);
          addToast(s.connected ? 'Connected to FastAPI' : 'Demo Mode Active', s.baseUrl);
        }}
      />

      {/* Floating Real-time Toast Notifications */}
      <div id="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.highRisk ? 'toast-high' : ''}`}>
            <span className="toast-icon">{t.highRisk ? '🚨' : '✨'}</span>
            <div>
              <div className="toast-title" style={{ fontWeight: 'bold' }}>{t.title}</div>
              <div className="toast-desc" style={{ fontSize: '0.85rem', color: '#ccc' }}>{t.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
