import React from 'react';

export type DashboardTab =
  | 'dashboard'
  | 'fraud_detection'
  | 'transactions'
  | 'analytics'
  | 'reports'
  | 'alerts'
  | 'users'
  | 'settings';

interface SidebarProps {
  activeTab: DashboardTab;
  onTabChange: (tab: DashboardTab) => void;
  openAlertsCount: number;
  onLogout: () => void;
  onViewLandingPage?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  openAlertsCount,
  onLogout,
  onViewLandingPage,
}) => {
  return (
    <aside className="dashboard-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand-header">
        <div className="sidebar-logo-icon">
          <svg viewBox="0 0 32 36" fill="none" width="26" height="30">
            <path
              d="M16 2 L28 7 C28 22 16 34 16 34 C16 34 4 22 4 7 Z"
              fill="#220408"
              stroke="#F5A623"
              strokeWidth="2"
            />
            {/* Miniature Fingerprint */}
            <circle cx="16" cy="17" r="5" stroke="#FF4D4D" strokeWidth="1.5" fill="none" />
            <path d="M12 17 A4 4 0 0 1 20 17" stroke="#FFD166" strokeWidth="1.5" fill="none" />
          </svg>
        </div>
        <div className="sidebar-brand-title">
          FraudShield <span className="gold-accent">AI</span>
        </div>
      </div>

      {/* Navigation Menu List */}
      <nav className="sidebar-menu">
        {/* Dashboard */}
        <button
          className={`sidebar-item ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => onTabChange('dashboard')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </span>
          <span className="sidebar-label">Dashboard</span>
        </button>

        {/* Fraud Detection / Predictor */}
        <button
          className={`sidebar-item ${activeTab === 'fraud_detection' ? 'active' : ''}`}
          onClick={() => onTabChange('fraud_detection')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="22" y1="12" x2="18" y2="12" />
              <line x1="6" y1="12" x2="2" y2="12" />
              <line x1="12" y1="6" x2="12" y2="2" />
              <line x1="12" y1="22" x2="12" y2="18" />
            </svg>
          </span>
          <span className="sidebar-label">Fraud Detection</span>
        </button>

        {/* Transactions */}
        <button
          className={`sidebar-item ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => onTabChange('transactions')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
              <line x1="1" y1="10" x2="23" y2="10" />
            </svg>
          </span>
          <span className="sidebar-label">Transactions</span>
        </button>

        {/* Analytics */}
        <button
          className={`sidebar-item ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => onTabChange('analytics')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
          </span>
          <span className="sidebar-label">Analytics</span>
        </button>

        {/* Reports */}
        <button
          className={`sidebar-item ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => onTabChange('reports')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </span>
          <span className="sidebar-label">Reports</span>
        </button>

        {/* Alerts with Badge */}
        <button
          className={`sidebar-item ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => onTabChange('alerts')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </span>
          <span className="sidebar-label">Alerts</span>
          {openAlertsCount > 0 && (
            <span className="sidebar-badge-count">{openAlertsCount}</span>
          )}
        </button>

        {/* Users */}
        <button
          className={`sidebar-item ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => onTabChange('users')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </span>
          <span className="sidebar-label">Users</span>
        </button>

        {/* Settings */}
        <button
          className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => onTabChange('settings')}
        >
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
          </span>
          <span className="sidebar-label">Settings</span>
        </button>

        {/* View Landing Page */}
        {onViewLandingPage && (
          <button className="sidebar-item" onClick={onViewLandingPage} style={{ marginTop: 'auto' }}>
            <span className="sidebar-icon">🌐</span>
            <span className="sidebar-label">Public Landing</span>
          </button>
        )}

        {/* Logout */}
        <button className="sidebar-item logout-item" onClick={onLogout} style={{ marginTop: onViewLandingPage ? '6px' : 'auto' }}>
          <span className="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </span>
          <span className="sidebar-label">Logout</span>
        </button>
      </nav>
    </aside>
  );
};
