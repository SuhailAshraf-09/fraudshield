import React from 'react';
import { AlertItem, DashboardSummary, TrendDataPoint } from '../types/api';

interface DashboardOverviewProps {
  summary: DashboardSummary;
  trends: TrendDataPoint[];
  alerts: AlertItem[];
  onViewAllAlerts: () => void;
  onUpgradeClick: () => void;
  onInvestigateAlert: (alert: AlertItem) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  summary,
  trends,
  alerts,
  onViewAllAlerts,
  onUpgradeClick,
  onInvestigateAlert,
}) => {
  return (
    <div className="dashboard-content-area">
      {/* Top Header Row */}
      <div className="dashboard-sub-header">
        <div className="sub-header-left">
          <div className="title-row">
            <span className="home-icon">🏠</span>
            <h2 className="overview-title">Dashboard Overview</h2>
          </div>
          <p className="overview-subtext">Real-time fraud monitoring and analytics</p>
        </div>

        <div className="sub-header-right">
          <div className="date-picker-button">
            <span className="cal-icon">📅</span>
            <span>Last 30 Days</span>
            <span className="down-arrow">˅</span>
          </div>
        </div>
      </div>

      {/* 4 Primary Metric Stat Cards */}
      <div className="metrics-cards-grid">
        {/* Card 1: Total Transactions */}
        <div className="stat-metric-card">
          <div className="metric-card-inner">
            <div className="card-left-col">
              <div className="metric-icon-small">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F5A623" strokeWidth="2">
                  <rect x="2" y="5" width="20" height="14" rx="2" />
                  <line x1="2" y1="10" x2="22" y2="10" />
                </svg>
              </div>
              <div className="metric-title-label">Total Transactions</div>
              <div className="metric-huge-value">
                {summary.total_transactions.toLocaleString()}
              </div>
              <div className="metric-trend-row positive">
                <span className="trend-arrow">↑</span>
                <span className="trend-pct">+12.5%</span>
              </div>
            </div>

            {/* Mini Sparkline Chart (Gold) */}
            <div className="card-right-sparkline">
              <svg viewBox="0 0 100 45" className="sparkline-svg">
                <path
                  d="M0 35 Q 25 15, 45 28 T 80 12 L 100 20"
                  fill="none"
                  stroke="#F5A623"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <circle cx="100" cy="20" r="3" fill="#FFE066" />
              </svg>
            </div>
          </div>
        </div>

        {/* Card 2: Fraud Detected (Glowing Red Accent) */}
        <div className="stat-metric-card card-fraud-detected">
          <div className="metric-card-inner">
            <div className="card-left-col">
              <div className="metric-icon-small icon-alert-shield">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FF4D4D" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <div className="metric-title-label">Fraud Detected</div>
              <div className="metric-huge-value text-red">
                {summary.flagged_transactions.toLocaleString()}
              </div>
              <div className="metric-trend-row alert-up">
                <span className="trend-arrow">↑</span>
                <span className="trend-pct">+8.3%</span>
              </div>
            </div>

            {/* Mini Sparkline Chart (Red) */}
            <div className="card-right-sparkline">
              <svg viewBox="0 0 100 45" className="sparkline-svg">
                <path
                  d="M0 30 Q 30 38, 55 22 T 85 10 L 100 22"
                  fill="none"
                  stroke="#FF2B4C"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <circle cx="100" cy="22" r="3" fill="#FF5252" />
              </svg>
            </div>
          </div>
        </div>

        {/* Card 3: Risk Rate */}
        <div className="stat-metric-card">
          <div className="metric-card-inner">
            <div className="card-left-col">
              <div className="metric-icon-small">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F5A623" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
              </div>
              <div className="metric-title-label">Risk Rate</div>
              <div className="metric-huge-value">
                {summary.risk_rate_percent || 1.03}%
              </div>
              <div className="metric-trend-row favorable-down">
                <span className="trend-arrow">↓</span>
                <span className="trend-pct">-0.21%</span>
              </div>
            </div>

            {/* Mini Sparkline Chart (Gold) */}
            <div className="card-right-sparkline">
              <svg viewBox="0 0 100 45" className="sparkline-svg">
                <path
                  d="M0 15 Q 35 32, 65 18 T 100 32"
                  fill="none"
                  stroke="#F5A623"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <circle cx="100" cy="32" r="3" fill="#FFE066" />
              </svg>
            </div>
          </div>
        </div>

        {/* Card 4: Active Users */}
        <div className="stat-metric-card">
          <div className="metric-card-inner">
            <div className="card-left-col">
              <div className="metric-icon-small">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F5A623" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
              </div>
              <div className="metric-title-label">Active Users</div>
              <div className="metric-huge-value">
                {(summary.active_users || 2540).toLocaleString()}
              </div>
              <div className="metric-trend-row positive">
                <span className="trend-arrow">↑</span>
                <span className="trend-pct">+15.7%</span>
              </div>
            </div>

            {/* Decorative User Glow Silhouette */}
            <div className="card-right-sparkline user-glow-box">
              <svg viewBox="0 0 60 50" width="55" height="45" fill="none">
                <circle cx="30" cy="18" r="12" fill="#F5A623" opacity="0.3" />
                <path d="M12 46 C12 34 20 28 30 28 C40 28 48 34 48 46" fill="#F5A623" opacity="0.25" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Main Analytics Row (Trends, Model Donut, Recent Alerts, Upgrade Card) */}
      <div className="dashboard-visual-grid">
        {/* Widget 1: Fraud Trends Dual-Line Chart */}
        <div className="grid-widget-box trends-widget">
          <div className="widget-header">
            <h3 className="widget-title">Fraud Trends</h3>
            <div className="chart-legend-row">
              <div className="legend-item">
                <span className="legend-dot dot-yellow" />
                <span className="legend-text">Legitimate</span>
              </div>
              <div className="legend-item">
                <span className="legend-dot dot-red" />
                <span className="legend-text">Fraudulent</span>
              </div>
            </div>
          </div>

          <div className="trends-chart-wrapper">
            <svg viewBox="0 0 520 220" className="trends-chart-svg" preserveAspectRatio="none">
              <defs>
                <linearGradient id="legitAreaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#F5A623" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#F5A623" stopOpacity="0" />
                </linearGradient>
                <linearGradient id="fraudAreaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF1744" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#FF1744" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="45" y1="30" x2="510" y2="30" stroke="#252532" strokeDasharray="3 3" />
              <line x1="45" y1="80" x2="510" y2="80" stroke="#252532" strokeDasharray="3 3" />
              <line x1="45" y1="130" x2="510" y2="130" stroke="#252532" strokeDasharray="3 3" />
              <line x1="45" y1="180" x2="510" y2="180" stroke="#252532" />

              {/* Y-Axis Labels */}
              <text x="15" y="34" fill="#666" fontSize="11" fontFamily="sans-serif">6K</text>
              <text x="15" y="84" fill="#666" fontSize="11" fontFamily="sans-serif">4K</text>
              <text x="15" y="134" fill="#666" fontSize="11" fontFamily="sans-serif">2K</text>
              <text x="25" y="184" fill="#666" fontSize="11" fontFamily="sans-serif">0</text>

              {/* Legitimate Curve (Yellow/Gold) */}
              <path
                d="M 50 145 C 90 120, 130 140, 170 100 C 210 60, 260 110, 310 90 C 360 70, 410 40, 460 55 L 505 50"
                fill="none"
                stroke="#FFD166"
                strokeWidth="3"
                strokeLinecap="round"
              />
              {/* Nodes for Legitimate */}
              <circle cx="50" cy="145" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />
              <circle cx="125" cy="130" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />
              <circle cx="200" cy="90" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />
              <circle cx="275" cy="105" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />
              <circle cx="350" cy="78" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />
              <circle cx="425" cy="46" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />
              <circle cx="505" cy="50" r="4.5" fill="#FFE066" stroke="#111" strokeWidth="2" />

              {/* Fraudulent Curve (Red) */}
              <path
                d="M 50 170 C 90 162, 130 165, 170 152 C 210 140, 260 160, 310 145 C 360 135, 410 125, 460 132 L 505 130"
                fill="none"
                stroke="#FF2B4C"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              {/* Nodes for Fraudulent */}
              <circle cx="50" cy="170" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />
              <circle cx="125" cy="165" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />
              <circle cx="200" cy="146" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />
              <circle cx="275" cy="155" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />
              <circle cx="350" cy="140" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />
              <circle cx="425" cy="128" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />
              <circle cx="505" cy="130" r="4" fill="#FF5252" stroke="#111" strokeWidth="1.5" />

              {/* X-Axis Days */}
              <text x="50" y="205" fill="#888" fontSize="11" textAnchor="middle">Mon</text>
              <text x="125" y="205" fill="#888" fontSize="11" textAnchor="middle">Tue</text>
              <text x="200" y="205" fill="#888" fontSize="11" textAnchor="middle">Wed</text>
              <text x="275" y="205" fill="#888" fontSize="11" textAnchor="middle">Thu</text>
              <text x="350" y="205" fill="#888" fontSize="11" textAnchor="middle">Fri</text>
              <text x="425" y="205" fill="#888" fontSize="11" textAnchor="middle">Sat</text>
              <text x="505" y="205" fill="#888" fontSize="11" textAnchor="middle">Sun</text>
            </svg>
          </div>
        </div>

        {/* Widget 2: Detection by Model Donut Chart */}
        <div className="grid-widget-box model-donut-widget">
          <div className="widget-header">
            <h3 className="widget-title">Detection by Model</h3>
          </div>

          <div className="donut-content-row">
            {/* Donut Chart SVG */}
            <div className="donut-svg-wrapper">
              <svg viewBox="0 0 160 160" width="130" height="130" className="donut-svg">
                {/* Background Ring */}
                <circle cx="80" cy="80" r="54" fill="none" stroke="#202028" strokeWidth="16" />
                
                {/* XGBoost Arc (Gold) ~34% */}
                <circle
                  cx="80"
                  cy="80"
                  r="54"
                  fill="none"
                  stroke="#FFD166"
                  strokeWidth="16"
                  strokeDasharray="115 224"
                  strokeDashoffset="0"
                  transform="rotate(-90 80 80)"
                />
                
                {/* Random Forest Arc (Red) ~32% */}
                <circle
                  cx="80"
                  cy="80"
                  r="54"
                  fill="none"
                  stroke="#FF2B4C"
                  strokeWidth="16"
                  strokeDasharray="108 231"
                  strokeDashoffset="-115"
                  transform="rotate(-90 80 80)"
                />

                {/* Isolation Forest Arc (White/Grey) ~34% */}
                <circle
                  cx="80"
                  cy="80"
                  r="54"
                  fill="none"
                  stroke="#E2E8F0"
                  strokeWidth="16"
                  strokeDasharray="115 224"
                  strokeDashoffset="-223"
                  transform="rotate(-90 80 80)"
                />

                {/* Center Content */}
                <text x="80" y="76" textAnchor="middle" fill="#FFFFFF" fontSize="15" fontWeight="bold">
                  96.7%
                </text>
                <text x="80" y="92" textAnchor="middle" fill="#A0A0B0" fontSize="9">
                  Accuracy
                </text>
              </svg>
            </div>

            {/* Model Legend List */}
            <div className="donut-legend-col">
              <div className="model-stat-row">
                <span className="dot dot-yellow" />
                <span className="model-name">XGBoost</span>
                <span className="model-pct">34%</span>
              </div>
              <div className="model-stat-row">
                <span className="dot dot-red" />
                <span className="model-name">Random Forest</span>
                <span className="model-pct">32%</span>
              </div>
              <div className="model-stat-row">
                <span className="dot dot-white" />
                <span className="model-name">Isolation Forest</span>
                <span className="model-pct">34%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Widget 3: Recent Alerts Feed */}
        <div className="grid-widget-box alerts-widget">
          <div className="widget-header">
            <h3 className="widget-title">Recent Alerts</h3>
            <button className="view-all-link-btn" onClick={onViewAllAlerts}>
              View All →
            </button>
          </div>

          <div className="recent-alerts-list">
            {alerts.slice(0, 3).map((item) => (
              <div
                key={item.id}
                className="alert-item-row"
                onClick={() => onInvestigateAlert(item)}
              >
                <div className="alert-badge-icon">
                  <span className="warning-tri">⚠️</span>
                </div>
                <div className="alert-info-col">
                  <div className="alert-line-title">
                    {item.notes || 'High Risk Transaction'}
                  </div>
                  {item.amount_display && (
                    <div className="alert-meta-sub">
                      Amount: <span className="text-gold">{item.amount_display}</span>
                    </div>
                  )}
                </div>
                <div className="alert-time-col">
                  {item.timestamp_display || 'Just now'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Widget 4: Upgrade Plan / Protection Promo Card */}
        <div className="grid-widget-box promo-plan-widget">
          <div className="promo-shield-glow">
            <svg viewBox="0 0 80 90" width="56" height="64" fill="none">
              <path
                d="M40 5 L72 18 C72 58 40 82 40 82 C40 82 8 58 8 18 Z"
                fill="#2A050B"
                stroke="#FFD166"
                strokeWidth="3.5"
              />
              <path
                d="M40 14 L62 24 C62 50 40 70 40 70 C40 70 18 50 18 24 Z"
                stroke="#FF2B4C"
                strokeWidth="1.5"
              />
              {/* Inner Fingerprint */}
              <circle cx="40" cy="40" r="10" stroke="#FFE066" strokeWidth="2" fill="none" />
            </svg>
          </div>

          <h4 className="promo-headline">Stay Protected with FraudShield AI</h4>
          <p className="promo-desc">Advanced AI. Maximum Security.</p>

          <button className="btn btn-gold upgrade-btn" onClick={onUpgradeClick}>
            Upgrade Plan →
          </button>
        </div>
      </div>
    </div>
  );
};
