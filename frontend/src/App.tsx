import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { LandingSections } from './components/LandingSections';
import { AuthPage } from './components/AuthPage';
import { Sidebar, DashboardTab } from './components/Sidebar';
import { DashboardOverview } from './components/DashboardOverview';
import { FraudDetectionSandbox } from './components/FraudDetectionSandbox';
import { TransactionsTable } from './components/TransactionsTable';
import { AlertsManager } from './components/AlertsManager';
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
  UserPublic,
} from './types/api';

export type AppView = 'landing' | 'auth' | 'dashboard';

export const App: React.FC = () => {
  // Navigation View: 'landing' (public), 'auth' (login/register), 'dashboard' (gated behind login)
  const [currentView, setCurrentView] = useState<AppView>('landing');
  const [authInitialMode, setAuthInitialMode] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState<DashboardTab>('dashboard');

  // Authenticated user state
  const [currentUser, setCurrentUser] = useState<UserPublic | null>(() => {
    return apiService.getStoredUser();
  });

  // Backend connection status
  const [apiStatus, setApiStatus] = useState<ApiStatus>({
    connected: false,
    mode: 'standalone_demo',
    baseUrl: apiService.getBaseUrl(),
  });

  // Dashboard Data states
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
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [liveStreamActive, setLiveStreamActive] = useState(true);
  const [toasts, setToasts] = useState<Array<{ id: string; title: string; desc: string; highRisk?: boolean }>>([]);

  // Toast Helper
  const addToast = (title: string, desc: string, highRisk = false) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev.slice(-3), { id, title, desc, highRisk }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  };

  // Load backend and dashboard data
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

  // Live Transaction Simulation Stream
  useEffect(() => {
    if (!liveStreamActive || currentView !== 'dashboard') return;

    const interval = setInterval(() => {
      const isRisk = Math.random() < 0.25;
      const amount = Math.floor(20 + Math.random() * 4500);
      const newTx: TransactionItem = {
        id: `TX_${Math.floor(1000 + Math.random() * 9000)}_${Math.random() < 0.5 ? 'US' : 'EU'}`,
        amount_minor: amount * 100,
        currency: 'USD',
        occurred_at: new Date().toISOString(),
        merchant_category: isRisk ? 'crypto_exchange' : 'online',
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
  }, [liveStreamActive, currentView]);

  // Handle protected dashboard navigation
  const navigateToDashboard = () => {
    if (!currentUser) {
      setAuthInitialMode('login');
      setCurrentView('auth');
      addToast('Authentication Required', 'Please sign in or register to access the Dashboard');
    } else {
      setCurrentView('dashboard');
    }
  };

  // Open Auth Page
  const openLogin = () => {
    setAuthInitialMode('login');
    setCurrentView('auth');
  };

  const openRegister = () => {
    setAuthInitialMode('register');
    setCurrentView('auth');
  };

  // Auth Success handler
  const handleAuthSuccess = (user: UserPublic) => {
    setCurrentUser(user);
    setCurrentView('dashboard');
    addToast('Welcome to FraudShield AI', `Signed in successfully as ${user.email} (${user.role.toUpperCase()})`);
  };

  // Logout handler
  const handleLogout = () => {
    apiService.logout();
    setCurrentUser(null);
    setCurrentView('landing');
    addToast('Logged Out', 'You have been safely signed out. Returning to home.');
  };

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

      {/* ===================================================================
          VIEW 1: PUBLIC LANDING PAGE (DEFAULT FOR ALL VISITORS)
          =================================================================== */}
      {currentView === 'landing' && (
        <div className="landing-view-flow">
          <Header
            currentUser={currentUser}
            onSignInClick={openLogin}
            onRegisterClick={openRegister}
            onGoToDashboard={navigateToDashboard}
            onLogout={handleLogout}
          />

          <Hero
            onExplorePlatform={navigateToDashboard}
            onWatchDemo={navigateToDashboard}
          />

          <LandingSections
            onGetStartedClick={openRegister}
            onExploreClick={navigateToDashboard}
          />
        </div>
      )}

      {/* ===================================================================
          VIEW 2: DEDICATED AUTHENTICATION PAGE (LOGIN & REGISTER)
          =================================================================== */}
      {currentView === 'auth' && (
        <AuthPage
          initialMode={authInitialMode}
          onAuthSuccess={handleAuthSuccess}
          onBackToHome={() => setCurrentView('landing')}
        />
      )}

      {/* ===================================================================
          VIEW 3: SECURE OPERATIONS & ADMIN DASHBOARD (AFTER LOGIN ONLY)
          =================================================================== */}
      {currentView === 'dashboard' && currentUser && (
        <section className="dashboard-section-wrapper" id="dashboard" style={{ paddingTop: '20px' }}>
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
              onLogout={handleLogout}
              onViewLandingPage={() => setCurrentView('landing')}
            />

            {/* Dashboard Main View Area */}
            <main className="dashboard-main-area">
              {/* Dashboard Top Header Bar (Search, Live Stream, Alerts, Admin profile) */}
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

                  {/* Backend Status indicator button */}
                  <button
                    className="backend-mini-pill"
                    onClick={() => setIsSettingsOpen(true)}
                    title="Configure backend server connection"
                  >
                    <span className={`status-dot ${apiStatus.connected ? 'online' : 'demo'}`} />
                    <span>{apiStatus.connected ? 'FastAPI Online' : 'Demo Engine'}</span>
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

                  {/* Authenticated User Profile */}
                  <div className="user-profile-pill" onClick={handleLogout} title="Click to Logout">
                    <div className="user-avatar-circle">
                      <span className="avatar-fallback">👤</span>
                    </div>
                    <div className="user-text-col">
                      <span className="user-name">{currentUser.email.split('@')[0]}</span>
                      <span className="user-badge-mini">{currentUser.role.toUpperCase()}</span>
                    </div>
                    <span className="dropdown-caret" title="Logout">🚪</span>
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
                    addToast('Enterprise Plan', 'Contact enterprise@fraudshield.ai for custom volume tiers');
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
                <div className="analytics-full-view glass-panel" style={{ margin: '24px', padding: '24px' }}>
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
                <div className="reports-view glass-panel" style={{ margin: '24px', padding: '24px' }}>
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
                <div className="users-view glass-panel" style={{ margin: '24px', padding: '24px' }}>
                  <h2 className="table-title">👥 Security Operations & Reviewer Team</h2>
                  <p className="table-subtitle">Assign fraud alert queues, reviewer permissions, and MFA policies</p>
                  <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div className="user-row-pill" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: 'rgba(255,255,255,0.04)', borderRadius: '8px' }}>
                      <span>👤 {currentUser.email}</span>
                      <span className="risk-badge badge-low">{currentUser.role.toUpperCase()}</span>
                    </div>
                    <div className="user-row-pill" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: 'rgba(255,255,255,0.04)', borderRadius: '8px' }}>
                      <span>👤 analyst@fraudshield.ai</span>
                      <span className="risk-badge badge-medium">ANALYST</span>
                    </div>
                  </div>
                </div>
              )}
            </main>
          </div>
        </section>
      )}

      {/* Backend Settings Modal */}
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
