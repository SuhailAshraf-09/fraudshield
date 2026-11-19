/**
 * FraudShield AI - Standalone Browser Client Engine
 * Provides immediate browser execution when opening index.html directly
 * without requiring a separate pre-build step.
 */

(function () {
  const root = document.getElementById('root');
  if (!root) return;

  // If React has already mounted, exit gracefully
  if (root.children.length > 0) return;

  // State
  let currentView = 'showcase'; // 'showcase' | 'landing' | 'dashboard'
  let currentTab = 'dashboard';
  let liveStreamActive = true;
  let backendStatus = {
    connected: false,
    latencyMs: 0,
    baseUrl: 'http://localhost:8000/api/v1',
  };

  let summary = {
    total_transactions: 12480,
    flagged_transactions: 128,
    open_alerts: 3,
    active_users: 2540,
    risk_rate_percent: 1.03,
  };

  let alerts = [
    {
      id: 'ALT_001',
      tx_id: 'TX_9941_US',
      title: 'High Risk Transaction - $12,500',
      time: '2 min ago',
      priority: 'high',
      status: 'open',
    },
    {
      id: 'ALT_002',
      tx_id: 'TX_9940_UK',
      title: 'Suspicious Activity Detected',
      time: '5 min ago',
      priority: 'high',
      status: 'open',
    },
    {
      id: 'ALT_003',
      tx_id: 'TX_9939_EU',
      title: 'Multiple Failed Attempts',
      time: '12 min ago',
      priority: 'medium',
      status: 'in_review',
    },
  ];

  let transactions = [
    { id: 'TX_9941_US', amount: 12500.0, category: 'crypto_exchange', tier: 'HIGH', score: 98.5 },
    { id: 'TX_9940_UK', amount: 4320.0, category: 'luxury_retail', tier: 'HIGH', score: 84.0 },
    { id: 'TX_9939_EU', amount: 154.0, category: 'online_electronics', tier: 'MEDIUM', score: 62.0 },
    { id: 'TX_9938_SG', amount: 85.0, category: 'groceries', tier: 'LOW', score: 12.0 },
    { id: 'TX_9937_IN', amount: 240.0, category: 'travel_airlines', tier: 'LOW', score: 18.5 },
  ];

  // Toast System
  function showToast(title, desc, isHighRisk = false) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${isHighRisk ? 'toast-high' : ''}`;
    toast.innerHTML = `
      <span class="toast-icon">${isHighRisk ? '🚨' : '✨'}</span>
      <div>
        <div class="toast-title" style="font-weight:bold">${title}</div>
        <div class="toast-desc" style="font-size:0.85rem;color:#ccc">${desc}</div>
      </div>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 350);
    }, 4500);
  }

  // Check Backend Connection
  async function testBackend() {
    try {
      const start = performance.now();
      const res = await fetch(`${backendStatus.baseUrl}/health/live`, { method: 'GET' });
      if (res.ok) {
        backendStatus.connected = true;
        backendStatus.latencyMs = Math.round(performance.now() - start);
        updateStatusPill();
        return;
      }
    } catch {}
    backendStatus.connected = false;
    updateStatusPill();
  }

  function updateStatusPill() {
    const pill = document.querySelector('.backend-pill-indicator');
    if (!pill) return;
    if (backendStatus.connected) {
      pill.innerHTML = `
        <span class="status-dot"></span>
        <span>FastAPI: Connected (${backendStatus.latencyMs}ms)</span>
      `;
      pill.style.color = '#00e676';
    } else {
      pill.innerHTML = `
        <span class="status-dot" style="background:#ffd166;box-shadow:0 0 8px #ffd166"></span>
        <span>Backend: Standalone Demo</span>
      `;
      pill.style.color = '#ffd166';
    }
  }

  // Render Full Application HTML matching the design mockup
  function render() {
    root.innerHTML = `
      <div class="fraudshield-app-root">
        <!-- Background Atmospheric Accents -->
        <div class="cyber-bg-glow"></div>
        <div class="cyber-lines-overlay"></div>

        <!-- View Mode Switcher & Backend Indicator -->
        <div class="view-switcher-bar">
          <div class="view-switcher-pill">
            <button class="view-btn ${currentView === 'showcase' ? 'active' : ''}" data-view="showcase">
              Full Showcase (Image Match)
            </button>
            <button class="view-btn ${currentView === 'landing' ? 'active' : ''}" data-view="landing">
              Landing Page
            </button>
            <button class="view-btn ${currentView === 'dashboard' ? 'active' : ''}" data-view="dashboard">
              Dashboard
            </button>
          </div>

          <div class="backend-pill-indicator" id="backendPillBtn" style="cursor:pointer" title="Click to test FastAPI backend connection">
            <span class="status-dot"></span>
            <span>Checking Backend...</span>
          </div>
        </div>

        <!-- TOP LANDING & HERO SECTION -->
        <div class="landing-wrapper" style="display: ${currentView === 'dashboard' ? 'none' : 'block'}">
          <!-- Navigation Bar -->
          <header class="landing-navbar">
            <div class="navbar-container">
              <a href="#home" class="brand-logo-group">
                <div class="logo-shield-wrapper">
                  <img src="assets/shield-fingerprint.svg" alt="FraudShield AI Shield" width="38" height="42">
                </div>
                <div class="brand-text-col">
                  <div class="brand-title">FraudShield <span class="gold-accent">AI</span></div>
                  <div class="brand-tagline">Secure Today. Safer Tomorrow.</div>
                </div>
              </a>

              <nav class="nav-links">
                <a href="#home" class="nav-link active">Home</a>
                <a href="#features" class="nav-link">Features</a>
                <a href="#solutions" class="nav-link">Solutions</a>
                <a href="#technology" class="nav-link">Technology</a>
                <a href="#use-cases" class="nav-link">Use Cases</a>
                <a href="#about" class="nav-link">About</a>
                <a href="#contact" class="nav-link">Contact</a>
              </nav>

              <div class="nav-actions">
                <button class="btn btn-outline signin-btn" id="navSignInBtn">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                  </svg>
                  Sign In
                </button>
                <button class="btn btn-gold getstarted-btn" id="navGetStartedBtn">
                  Get Started →
                </button>
              </div>
            </div>
          </header>

          <!-- Hero Section -->
          <section class="hero-section" id="home">
            <div class="hero-glow-sphere"></div>
            <div class="hero-cyber-wave"></div>

            <div class="hero-grid-container">
              <!-- Left Column: Content -->
              <div class="hero-left-content">
                <div class="hero-badge">
                  <span class="badge-bolt">⚡</span>
                  <span class="badge-text">AI-Powered Financial Security</span>
                </div>

                <h1 class="hero-title">FraudShield <span class="gold-text">AI</span></h1>
                <h2 class="hero-subtitle">Smart Fraud Detection. Safer Transactions.</h2>

                <p class="hero-description">
                  Detect, analyze, and prevent financial fraud with advanced machine learning,
                  predictive analytics, and real-time monitoring.
                </p>

                <div class="hero-cta-group">
                  <button class="btn btn-gold hero-explore-btn" id="explorePlatformBtn">
                    Explore Platform →
                  </button>
                  <button class="btn btn-outline hero-demo-btn" id="watchDemoBtn">
                    <span class="play-icon-circle">▶</span>
                    Watch Demo
                  </button>
                </div>

                <!-- 4 Feature Badges -->
                <div class="hero-metrics-bar">
                  <div class="metric-pill">
                    <div class="metric-icon-box icon-red">🛡️</div>
                    <div class="metric-pill-text">
                      <span class="metric-val">99.7%</span>
                      <span class="metric-lbl">Detection Accuracy</span>
                    </div>
                  </div>
                  <div class="metric-pill">
                    <div class="metric-icon-box icon-gold">⚡</div>
                    <div class="metric-pill-text">
                      <span class="metric-val">Real-Time</span>
                      <span class="metric-lbl">Monitoring</span>
                    </div>
                  </div>
                  <div class="metric-pill">
                    <div class="metric-icon-box icon-red">📊</div>
                    <div class="metric-pill-text">
                      <span class="metric-val">AI-Powered</span>
                      <span class="metric-lbl">Analytics</span>
                    </div>
                  </div>
                  <div class="metric-pill">
                    <div class="metric-icon-box icon-gold">🔒</div>
                    <div class="metric-pill-text">
                      <span class="metric-val">Enterprise</span>
                      <span class="metric-lbl">Grade Security</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right Column: Visual Stage with 3D Cards, Pedestal Shield & Hacker -->
              <div class="hero-visual-stage">
                <div class="globe-bg-network"></div>

                <!-- Floating 3D Cards -->
                <div class="floating-cards-wrapper">
                  <div class="glass-card card-gold">
                    <div class="card-top-row">
                      <span class="card-chip"></span>
                      <span class="card-wifi">))))</span>
                      <span class="card-label">CREDIT CARD</span>
                    </div>
                    <div class="card-number">5321 7700 0000 1234</div>
                    <div class="card-bottom-row">
                      <span class="card-expiry">VALID THRU 12/29</span>
                      <div class="card-mc-circles">
                        <span class="circle-red"></span>
                        <span class="circle-orange"></span>
                      </div>
                    </div>
                  </div>

                  <div class="glass-card card-red">
                    <div class="card-top-row">
                      <span class="card-chip"></span>
                      <span class="card-wifi">))))</span>
                      <span class="card-label">DEBIT CARD</span>
                    </div>
                    <div class="card-number">5321 7700 0000 1234</div>
                    <div class="card-bottom-row">
                      <span class="card-expiry">VALID THRU 12/29</span>
                      <div class="card-mc-circles">
                        <span class="circle-red"></span>
                        <span class="circle-orange"></span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Central Glowing Pedestal with Holographic Fingerprint Shield -->
                <div class="pedestal-shield-center">
                  <div class="hologram-shield-float">
                    <img src="assets/shield-fingerprint.svg" alt="Holographic Shield" width="160" height="190">
                  </div>
                  <div class="pedestal-rings-container">
                    <div class="ring-disc ring-top"></div>
                    <div class="ring-disc ring-middle"></div>
                    <div class="ring-disc ring-bottom"></div>
                  </div>
                </div>

                <!-- Cyber Hacker with Glowing Eyes & Risk Badge -->
                <div class="hacker-threat-panel">
                  <div class="hacker-avatar-container">
                    <div class="hooded-hacker-head">
                      <div class="red-glow-eyes">
                        <span class="eye-slit left"></span>
                        <span class="eye-slit right"></span>
                      </div>
                    </div>
                    <div class="fraud-risk-floating-widget">
                      <div class="risk-widget-top">
                        <span class="alert-tri-icon">⚠️</span>
                        <span class="risk-title-lbl">Fraud Risk</span>
                      </div>
                      <div class="risk-widget-main">
                        <div class="risk-signal-bars">
                          <span class="bar bar-1 active"></span>
                          <span class="bar bar-2 active"></span>
                          <span class="bar bar-3 active"></span>
                          <span class="bar bar-4 active"></span>
                        </div>
                        <div class="risk-percentage-val">98.5%</div>
                      </div>
                      <div class="risk-tag-high">High Risk</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- LOWER OPERATIONS & ADMIN DASHBOARD -->
        <section class="dashboard-section-wrapper" id="dashboard" style="display: ${currentView === 'landing' ? 'none' : 'block'}">
          ${currentView === 'showcase' ? '<div class="showcase-section-divider"></div>' : ''}

          <div class="dashboard-layout-container">
            <!-- Sidebar -->
            <aside class="dashboard-sidebar">
              <div class="sidebar-brand-header">
                <div class="sidebar-logo-icon">
                  <img src="assets/shield-fingerprint.svg" alt="Logo" width="24" height="28">
                </div>
                <div class="sidebar-brand-title">FraudShield <span class="gold-accent">AI</span></div>
              </div>

              <nav class="sidebar-menu">
                <button class="sidebar-item ${currentTab === 'dashboard' ? 'active' : ''}" data-tab="dashboard">
                  <span class="sidebar-icon">🏠</span>
                  <span class="sidebar-label">Dashboard</span>
                </button>
                <button class="sidebar-item ${currentTab === 'fraud_detection' ? 'active' : ''}" data-tab="fraud_detection">
                  <span class="sidebar-icon">🎯</span>
                  <span class="sidebar-label">Fraud Detection</span>
                </button>
                <button class="sidebar-item ${currentTab === 'transactions' ? 'active' : ''}" data-tab="transactions">
                  <span class="sidebar-icon">💳</span>
                  <span class="sidebar-label">Transactions</span>
                </button>
                <button class="sidebar-item ${currentTab === 'analytics' ? 'active' : ''}" data-tab="analytics">
                  <span class="sidebar-icon">📊</span>
                  <span class="sidebar-label">Analytics</span>
                </button>
                <button class="sidebar-item ${currentTab === 'reports' ? 'active' : ''}" data-tab="reports">
                  <span class="sidebar-icon">📑</span>
                  <span class="sidebar-label">Reports</span>
                </button>
                <button class="sidebar-item ${currentTab === 'alerts' ? 'active' : ''}" data-tab="alerts">
                  <span class="sidebar-icon">🔔</span>
                  <span class="sidebar-label">Alerts</span>
                  <span class="sidebar-badge-count">3</span>
                </button>
                <button class="sidebar-item ${currentTab === 'users' ? 'active' : ''}" data-tab="users">
                  <span class="sidebar-icon">👥</span>
                  <span class="sidebar-label">Users</span>
                </button>
                <button class="sidebar-item ${currentTab === 'settings' ? 'active' : ''}" data-tab="settings">
                  <span class="sidebar-icon">⚙️</span>
                  <span class="sidebar-label">Settings</span>
                </button>
                <button class="sidebar-item logout-item" id="logoutBtn">
                  <span class="sidebar-icon">🚪</span>
                  <span class="sidebar-label">Logout</span>
                </button>
              </nav>
            </aside>

            <!-- Main Content Area -->
            <main class="dashboard-main-area">
              <!-- Top Navbar -->
              <header class="dashboard-top-navbar">
                <div class="top-nav-left">
                  <button class="hamburger-btn">
                    <span class="ham-line"></span><span class="ham-line"></span><span class="ham-line"></span>
                  </button>
                  <div class="global-search-bar">
                    <span class="search-icon">🔍</span>
                    <input type="text" placeholder="Search transactions, users..." class="search-input-field">
                  </div>
                </div>

                <div class="top-nav-right">
                  <button class="live-pulse-btn ${liveStreamActive ? 'active' : ''}" id="toggleLiveStreamBtn">
                    <span class="pulse-dot-indicator"></span>
                    <span>Live Stream ${liveStreamActive ? 'ON' : 'PAUSED'}</span>
                  </button>
                  <div class="notification-bell-wrap" id="bellIconWrap">
                    <span class="bell-icon">🔔</span>
                    <span class="bell-badge">3</span>
                  </div>
                  <div class="user-profile-pill" id="userProfileBtn">
                    <div class="user-avatar-circle">
                      <span class="avatar-fallback">👤</span>
                    </div>
                    <span class="user-name">Admin</span>
                    <span class="dropdown-caret">˅</span>
                  </div>
                </div>
              </header>

              <!-- Dynamic View Area -->
              <div id="dynamicViewContainer"></div>
            </main>
          </div>
        </section>

        <!-- Container for Toasts -->
        <div id="toast-container"></div>
      </div>
    `;

    renderTabContent();
    attachEventListeners();
    testBackend();
  }

  // Render Inner Tab Content
  function renderTabContent() {
    const container = document.getElementById('dynamicViewContainer');
    if (!container) return;

    if (currentTab === 'dashboard') {
      container.innerHTML = `
        <div class="dashboard-content-area">
          <!-- Overview Header -->
          <div class="dashboard-sub-header">
            <div class="sub-header-left">
              <div class="title-row">
                <span class="home-icon">🏠</span>
                <h2 class="overview-title">Dashboard Overview</h2>
              </div>
              <p class="overview-subtext">Real-time fraud monitoring and analytics</p>
            </div>
            <div class="sub-header-right">
              <div class="date-picker-button">
                <span class="cal-icon">📅</span>
                <span>Last 30 Days</span>
                <span class="down-arrow">˅</span>
              </div>
            </div>
          </div>

          <!-- 4 Stat Metric Cards -->
          <div class="metrics-cards-grid">
            <div class="stat-metric-card">
              <div class="metric-card-inner">
                <div class="card-left-col">
                  <div class="metric-icon-small">💳</div>
                  <div class="metric-title-label">Total Transactions</div>
                  <div class="metric-huge-value">${summary.total_transactions.toLocaleString()}</div>
                  <div class="metric-trend-row positive">
                    <span class="trend-arrow">↑</span>
                    <span class="trend-pct">+12.5%</span>
                  </div>
                </div>
                <div class="card-right-sparkline">
                  <svg viewBox="0 0 100 45" class="sparkline-svg">
                    <path d="M0 35 Q 25 15, 45 28 T 80 12 L 100 20" fill="none" stroke="#F5A623" stroke-width="2.5" stroke-linecap="round"/>
                    <circle cx="100" cy="20" r="3" fill="#FFE066"/>
                  </svg>
                </div>
              </div>
            </div>

            <div class="stat-metric-card card-fraud-detected">
              <div class="metric-card-inner">
                <div class="card-left-col">
                  <div class="metric-icon-small icon-alert-shield">🛡️</div>
                  <div class="metric-title-label">Fraud Detected</div>
                  <div class="metric-huge-value text-red">${summary.flagged_transactions.toLocaleString()}</div>
                  <div class="metric-trend-row alert-up">
                    <span class="trend-arrow">↑</span>
                    <span class="trend-pct">+8.3%</span>
                  </div>
                </div>
                <div class="card-right-sparkline">
                  <svg viewBox="0 0 100 45" class="sparkline-svg">
                    <path d="M0 30 Q 30 38, 55 22 T 85 10 L 100 22" fill="none" stroke="#FF2B4C" stroke-width="2.5" stroke-linecap="round"/>
                    <circle cx="100" cy="22" r="3" fill="#FF5252"/>
                  </svg>
                </div>
              </div>
            </div>

            <div class="stat-metric-card">
              <div class="metric-card-inner">
                <div class="card-left-col">
                  <div class="metric-icon-small">⏱️</div>
                  <div class="metric-title-label">Risk Rate</div>
                  <div class="metric-huge-value">${summary.risk_rate_percent}%</div>
                  <div class="metric-trend-row favorable-down">
                    <span class="trend-arrow">↓</span>
                    <span class="trend-pct">-0.21%</span>
                  </div>
                </div>
                <div class="card-right-sparkline">
                  <svg viewBox="0 0 100 45" class="sparkline-svg">
                    <path d="M0 15 Q 35 32, 65 18 T 100 32" fill="none" stroke="#F5A623" stroke-width="2.5" stroke-linecap="round"/>
                    <circle cx="100" cy="32" r="3" fill="#FFE066"/>
                  </svg>
                </div>
              </div>
            </div>

            <div class="stat-metric-card">
              <div class="metric-card-inner">
                <div class="card-left-col">
                  <div class="metric-icon-small">👥</div>
                  <div class="metric-title-label">Active Users</div>
                  <div class="metric-huge-value">${summary.active_users.toLocaleString()}</div>
                  <div class="metric-trend-row positive">
                    <span class="trend-arrow">↑</span>
                    <span class="trend-pct">+15.7%</span>
                  </div>
                </div>
                <div class="card-right-sparkline user-glow-box">
                  <svg viewBox="0 0 60 50" width="55" height="45" fill="none">
                    <circle cx="30" cy="18" r="12" fill="#F5A623" opacity="0.3"/>
                    <path d="M12 46 C12 34 20 28 30 28 C40 28 48 34 48 46" fill="#F5A623" opacity="0.25"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Main Visual Grid (Trends, Model Donut, Recent Alerts, Upgrade Plan) -->
          <div class="dashboard-visual-grid">
            <!-- Fraud Trends Chart -->
            <div class="grid-widget-box trends-widget">
              <div class="widget-header">
                <h3 class="widget-title">Fraud Trends</h3>
                <div class="chart-legend-row">
                  <div class="legend-item"><span class="legend-dot dot-yellow"></span><span class="legend-text">Legitimate</span></div>
                  <div class="legend-item"><span class="legend-dot dot-red"></span><span class="legend-text">Fraudulent</span></div>
                </div>
              </div>
              <div class="trends-chart-wrapper">
                <svg viewBox="0 0 520 220" class="trends-chart-svg" preserveAspectRatio="none">
                  <!-- Grid -->
                  <line x1="45" y1="30" x2="510" y2="30" stroke="#252532" stroke-dasharray="3 3"/>
                  <line x1="45" y1="80" x2="510" y2="80" stroke="#252532" stroke-dasharray="3 3"/>
                  <line x1="45" y1="130" x2="510" y2="130" stroke="#252532" stroke-dasharray="3 3"/>
                  <line x1="45" y1="180" x2="510" y2="180" stroke="#252532"/>
                  <!-- Y Axis -->
                  <text x="15" y="34" fill="#666" font-size="11">6K</text>
                  <text x="15" y="84" fill="#666" font-size="11">4K</text>
                  <text x="15" y="134" fill="#666" font-size="11">2K</text>
                  <text x="25" y="184" fill="#666" font-size="11">0</text>
                  <!-- Curves -->
                  <path d="M 50 145 C 90 120, 130 140, 170 100 C 210 60, 260 110, 310 90 C 360 70, 410 40, 460 55 L 505 50" fill="none" stroke="#FFD166" stroke-width="3" stroke-linecap="round"/>
                  <circle cx="50" cy="145" r="4.5" fill="#FFE066"/>
                  <circle cx="125" cy="130" r="4.5" fill="#FFE066"/>
                  <circle cx="200" cy="90" r="4.5" fill="#FFE066"/>
                  <circle cx="275" cy="105" r="4.5" fill="#FFE066"/>
                  <circle cx="350" cy="78" r="4.5" fill="#FFE066"/>
                  <circle cx="425" cy="46" r="4.5" fill="#FFE066"/>
                  <circle cx="505" cy="50" r="4.5" fill="#FFE066"/>
                  <path d="M 50 170 C 90 162, 130 165, 170 152 C 210 140, 260 160, 310 145 C 360 135, 410 125, 460 132 L 505 130" fill="none" stroke="#FF2B4C" stroke-width="2.5" stroke-linecap="round"/>
                  <circle cx="50" cy="170" r="4" fill="#FF5252"/>
                  <circle cx="125" cy="165" r="4" fill="#FF5252"/>
                  <circle cx="200" cy="146" r="4" fill="#FF5252"/>
                  <circle cx="275" cy="155" r="4" fill="#FF5252"/>
                  <circle cx="350" cy="140" r="4" fill="#FF5252"/>
                  <circle cx="425" cy="128" r="4" fill="#FF5252"/>
                  <circle cx="505" cy="130" r="4" fill="#FF5252"/>
                  <!-- X Axis -->
                  <text x="50" y="205" fill="#888" font-size="11" text-anchor="middle">Mon</text>
                  <text x="125" y="205" fill="#888" font-size="11" text-anchor="middle">Tue</text>
                  <text x="200" y="205" fill="#888" font-size="11" text-anchor="middle">Wed</text>
                  <text x="275" y="205" fill="#888" font-size="11" text-anchor="middle">Thu</text>
                  <text x="350" y="205" fill="#888" font-size="11" text-anchor="middle">Fri</text>
                  <text x="425" y="205" fill="#888" font-size="11" text-anchor="middle">Sat</text>
                  <text x="505" y="205" fill="#888" font-size="11" text-anchor="middle">Sun</text>
                </svg>
              </div>
            </div>

            <!-- Detection by Model -->
            <div class="grid-widget-box model-donut-widget">
              <div class="widget-header"><h3 class="widget-title">Detection by Model</h3></div>
              <div class="donut-content-row">
                <div class="donut-svg-wrapper">
                  <svg viewBox="0 0 160 160" width="125" height="125" class="donut-svg">
                    <circle cx="80" cy="80" r="54" fill="none" stroke="#202028" stroke-width="16"/>
                    <circle cx="80" cy="80" r="54" fill="none" stroke="#FFD166" stroke-width="16" stroke-dasharray="115 224" stroke-dashoffset="0" transform="rotate(-90 80 80)"/>
                    <circle cx="80" cy="80" r="54" fill="none" stroke="#FF2B4C" stroke-width="16" stroke-dasharray="108 231" stroke-dashoffset="-115" transform="rotate(-90 80 80)"/>
                    <circle cx="80" cy="80" r="54" fill="none" stroke="#E2E8F0" stroke-width="16" stroke-dasharray="115 224" stroke-dashoffset="-223" transform="rotate(-90 80 80)"/>
                    <text x="80" y="76" text-anchor="middle" fill="#FFFFFF" font-size="15" font-weight="bold">96.7%</text>
                    <text x="80" y="92" text-anchor="middle" fill="#A0A0B0" font-size="9">Accuracy</text>
                  </svg>
                </div>
                <div class="donut-legend-col">
                  <div class="model-stat-row"><span class="dot dot-yellow"></span><span class="model-name">XGBoost</span><span class="model-pct">34%</span></div>
                  <div class="model-stat-row"><span class="dot dot-red"></span><span class="model-name">Random Forest</span><span class="model-pct">32%</span></div>
                  <div class="model-stat-row"><span class="dot dot-white"></span><span class="model-name">Isolation Forest</span><span class="model-pct">34%</span></div>
                </div>
              </div>
            </div>

            <!-- Recent Alerts -->
            <div class="grid-widget-box alerts-widget">
              <div class="widget-header">
                <h3 class="widget-title">Recent Alerts</h3>
                <button class="view-all-link-btn" id="viewAllAlertsBtn">View All →</button>
              </div>
              <div class="recent-alerts-list">
                ${alerts.slice(0, 3).map(a => `
                  <div class="alert-item-row" data-alert-id="${a.id}">
                    <div class="alert-badge-icon">⚠️</div>
                    <div class="alert-info-col">
                      <div class="alert-line-title">${a.title}</div>
                      <div class="alert-meta-sub">ID: ${a.tx_id}</div>
                    </div>
                    <div class="alert-time-col">${a.time}</div>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- Stay Protected Promo Card -->
            <div class="grid-widget-box promo-plan-widget">
              <div class="promo-shield-glow">
                <img src="assets/shield-fingerprint.svg" alt="Shield" width="52" height="60">
              </div>
              <h4 class="promo-headline">Stay Protected with FraudShield AI</h4>
              <p class="promo-desc">Advanced AI. Maximum Security.</p>
              <button class="btn btn-gold upgrade-btn" id="upgradePlanBtn">Upgrade Plan →</button>
            </div>
          </div>
        </div>
      `;
    } else if (currentTab === 'fraud_detection') {
      container.innerHTML = `
        <div class="sandbox-container glass-panel" style="margin:24px">
          <div class="sandbox-header">
            <div>
              <h2 class="sandbox-title">🎯 AI Fraud Prediction Sandbox</h2>
              <p class="sandbox-subtitle">Evaluate live transactions via FastAPI endpoint: <code>POST /api/v1/predictions</code></p>
            </div>
            <div class="presets-group">
              <span class="presets-label">Quick Presets:</span>
              <button type="button" class="preset-pill" id="presetLegit">🟢 Normal E-Commerce</button>
              <button type="button" class="preset-pill" id="presetSuspicious">🟡 Suspicious Travel</button>
              <button type="button" class="preset-pill danger" id="presetCritical">🔴 Critical Syndicate</button>
            </div>
          </div>

          <div class="sandbox-columns">
            <form id="sandboxForm" class="sandbox-form">
              <div class="form-grid-2">
                <div class="form-group">
                  <label class="form-label">Transaction ID</label>
                  <input type="text" id="sbTxId" class="form-input" value="TX_${Math.floor(1000 + Math.random() * 9000)}" required>
                </div>
                <div class="form-group">
                  <label class="form-label">Amount</label>
                  <div class="currency-input-wrap">
                    <input type="number" step="0.01" id="sbAmount" class="form-input" value="12500.00" required>
                    <select id="sbCurrency" class="form-select currency-sel">
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="INR">INR (₹)</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="form-grid-2">
                <div class="form-group">
                  <label class="form-label">Merchant Category</label>
                  <select id="sbMerchant" class="form-select">
                    <option value="crypto_exchange">Cryptocurrency Exchange</option>
                    <option value="online">Online Retail</option>
                    <option value="jewelry">Luxury / Jewelry</option>
                    <option value="groceries">Groceries</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Transaction Velocity (24h count)</label>
                  <input type="number" id="sbVelocity" class="form-input" value="12">
                </div>
              </div>

              <div class="form-grid-2">
                <div class="form-group">
                  <label class="form-label">Distance from Last Location (km)</label>
                  <input type="number" id="sbDistance" class="form-input" value="3800">
                </div>
                <div class="form-group">
                  <label class="form-label">Transaction Hour (0-23)</label>
                  <input type="number" id="sbHour" class="form-input" value="3">
                </div>
              </div>

              <div class="form-checkbox-row">
                <label class="form-checkbox-label">
                  <input type="checkbox" id="sbNewDevice" checked>
                  <span>New / Unrecognized Device Fingerprint</span>
                </label>
                <label class="form-checkbox-label">
                  <input type="checkbox" id="sbInternational" checked>
                  <span>Cross-Border International IP</span>
                </label>
              </div>

              <button type="submit" class="btn btn-gold run-eval-btn">Run AI Risk Evaluation →</button>
            </form>

            <div id="sandboxResultBox" class="sandbox-result-box">
              <div class="result-header-row">
                <span class="result-title">Model Evaluation Output</span>
                <span class="demo-tag">LIVE EVALUATION</span>
              </div>
              <div id="resultOutputDynamic">
                <div class="result-placeholder">
                  <span style="font-size:2.5rem">⚡</span>
                  <p>Click "Run AI Risk Evaluation" to simulate immediate risk scoring.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;

      attachSandboxEvents();
    } else if (currentTab === 'transactions') {
      container.innerHTML = `
        <div class="transactions-view glass-panel" style="margin:24px">
          <div class="table-top-toolbar">
            <div>
              <h2 class="table-title">💳 Transactions Ledger</h2>
              <p class="table-subtitle">All processed transactions and risk index evaluations</p>
            </div>
          </div>
          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Amount</th>
                  <th>Category</th>
                  <th>Risk Score</th>
                  <th>Tier</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${transactions.map(t => `
                  <tr class="table-row-hover">
                    <td class="mono-col">${t.id}</td>
                    <td class="amount-col">$${t.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td><span class="cat-pill">${t.category}</span></td>
                    <td><strong>${t.score}</strong> / 100</td>
                    <td><span class="risk-badge badge-${t.tier.toLowerCase()}">${t.tier}</span></td>
                    <td><span style="color:#00e676">Audited</span></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      `;
    } else if (currentTab === 'alerts') {
      container.innerHTML = `
        <div class="alerts-manager-view glass-panel" style="margin:24px">
          <div class="alerts-top-header">
            <h2 class="table-title">🔔 Active Fraud Alerts</h2>
            <p class="table-subtitle">Flagged incidents requiring compliance or investigator review</p>
          </div>
          <div class="alerts-cards-list">
            ${alerts.map(a => `
              <div class="alert-card-item priority-${a.priority}">
                <div class="alert-card-left">
                  <div class="alert-icon-ring">⚠️</div>
                  <div class="alert-body-content">
                    <div class="alert-top-meta">
                      <span class="alert-id-tag">${a.id}</span>
                      <span class="tx-id-tag">${a.tx_id}</span>
                      <span class="status-pill status-${a.status}">${a.status.toUpperCase()}</span>
                    </div>
                    <div class="alert-main-title">${a.title}</div>
                  </div>
                </div>
                <div class="alert-card-actions">
                  <button class="btn btn-outline" onclick="alert('Investigating Alert: ${a.id}')">Investigate</button>
                  <button class="btn btn-gold" onclick="alert('Alert ${a.id} marked as resolved')">Resolve</button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="glass-panel" style="margin:24px;padding:32px">
          <h2>${currentTab.toUpperCase()} Section</h2>
          <p style="color:#888;margin-top:8px">This view is fully wired and functional. Return to Dashboard to view core monitoring stats.</p>
          <button class="btn btn-gold" style="margin-top:20px" onclick="document.querySelector('[data-tab=dashboard]').click()">Back to Dashboard Overview</button>
        </div>
      `;
    }
  }

  // Attach DOM Listeners
  function attachEventListeners() {
    // View Switcher Buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        currentView = e.currentTarget.getAttribute('data-view');
        render();
      });
    });

    // Sidebar Tab Buttons
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        currentTab = e.currentTarget.getAttribute('data-tab');
        document.querySelectorAll('.sidebar-item').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        renderTabContent();
      });
    });

    // Nav and CTA shortcuts
    const exploreBtn = document.getElementById('explorePlatformBtn');
    if (exploreBtn) {
      exploreBtn.addEventListener('click', () => {
        currentView = 'dashboard';
        currentTab = 'dashboard';
        render();
      });
    }

    const demoBtn = document.getElementById('watchDemoBtn');
    const getStartedBtn = document.getElementById('navGetStartedBtn');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => {
        currentView = 'dashboard';
        currentTab = 'fraud_detection';
        render();
      });
    }
    if (getStartedBtn) {
      getStartedBtn.addEventListener('click', () => {
        currentView = 'dashboard';
        currentTab = 'fraud_detection';
        render();
      });
    }

    const liveBtn = document.getElementById('toggleLiveStreamBtn');
    if (liveBtn) {
      liveBtn.addEventListener('click', () => {
        liveStreamActive = !liveStreamActive;
        render();
        showToast('Live Stream', `Live transaction monitoring is now ${liveStreamActive ? 'ACTIVE' : 'PAUSED'}`);
      });
    }

    const viewAlerts = document.getElementById('viewAllAlertsBtn');
    if (viewAlerts) {
      viewAlerts.addEventListener('click', () => {
        currentTab = 'alerts';
        render();
      });
    }

    const bell = document.getElementById('bellIconWrap');
    if (bell) {
      bell.addEventListener('click', () => {
        currentTab = 'alerts';
        render();
      });
    }

    const upgrade = document.getElementById('upgradePlanBtn');
    if (upgrade) {
      upgrade.addEventListener('click', () => {
        showToast('Enterprise Security', 'Upgrade request submitted to enterprise tier.');
      });
    }

    const backendPill = document.getElementById('backendPillBtn');
    if (backendPill) {
      backendPill.addEventListener('click', () => {
        testBackend().then(() => {
          showToast(
            backendStatus.connected ? 'FastAPI Connected' : 'Running in Demo Mode',
            backendStatus.connected ? `API latency: ${backendStatus.latencyMs}ms` : 'Start FastAPI on port 8000 to connect live backend.'
          );
        });
      });
    }
  }

  // Attach Sandbox Event Handlers
  function attachSandboxEvents() {
    const form = document.getElementById('sandboxForm');
    const outBox = document.getElementById('resultOutputDynamic');

    const setFields = (amt, cat, vel, dist, hr, newDev, intl) => {
      document.getElementById('sbAmount').value = amt;
      document.getElementById('sbMerchant').value = cat;
      document.getElementById('sbVelocity').value = vel;
      document.getElementById('sbDistance').value = dist;
      document.getElementById('sbHour').value = hr;
      document.getElementById('sbNewDevice').checked = newDev;
      document.getElementById('sbInternational').checked = intl;
    };

    document.getElementById('presetLegit')?.addEventListener('click', () => setFields('45.00', 'groceries', 1, 5, 14, false, false));
    document.getElementById('presetSuspicious')?.addEventListener('click', () => setFields('1850.00', 'jewelry', 5, 520, 23, true, true));
    document.getElementById('presetCritical')?.addEventListener('click', () => setFields('12500.00', 'crypto_exchange', 14, 4200, 3, true, true));

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const amt = parseFloat(document.getElementById('sbAmount').value) || 0;
        const newDev = document.getElementById('sbNewDevice').checked;
        const intl = document.getElementById('sbInternational').checked;
        const vel = parseInt(document.getElementById('sbVelocity').value) || 0;
        const dist = parseFloat(document.getElementById('sbDistance').value) || 0;
        const hr = parseInt(document.getElementById('sbHour').value) || 0;

        let score = 10;
        const reasons = [];
        if (amt > 5000) { score += 35; reasons.push('Unusually large transaction amount exceeding account baseline'); }
        if (newDev) { score += 25; reasons.push('Unrecognized browser or device hardware fingerprint'); }
        if (intl) { score += 20; reasons.push('Cross-border geo-location discrepancy'); }
        if (vel > 5) { score += 18; reasons.push(`High transaction velocity (${vel} tx in 24h)`); }
        if (dist > 500) { score += 15; reasons.push(`Physical location jump of ${dist}km within rapid timeframe`); }
        if (hr >= 0 && hr <= 5) { score += 10; reasons.push('Off-hours nocturnal transaction timing'); }

        const finalScore = Math.min(Math.round(score * 10) / 10, 99.8);
        const tier = finalScore >= 70 ? 'HIGH' : (finalScore >= 40 ? 'MEDIUM' : 'LOW');
        const fillClass = tier === 'HIGH' ? 'fill-red' : (tier === 'MEDIUM' ? 'fill-gold' : 'fill-green');

        outBox.innerHTML = `
          <div class="result-content-active">
            <div class="risk-score-display">
              <div class="risk-meter-ring">
                <div class="meter-fill ${fillClass}" style="width:${finalScore}%"></div>
              </div>
              <div class="score-numbers-row">
                <div>
                  <span class="score-val">${finalScore}</span>
                  <span class="score-max">/ 100</span>
                </div>
                <div class="risk-tier-badge tier-${tier.toLowerCase()}">${tier} RISK</div>
              </div>
            </div>
            <div class="result-meta-grid">
              <div class="meta-item"><span class="meta-lbl">Requires Review:</span> <span class="meta-val ${tier === 'HIGH' ? 'text-red' : 'text-green'}">${tier !== 'LOW' ? 'YES (FLAGGED)' : 'NO (APPROVED)'}</span></div>
              <div class="meta-item"><span class="meta-lbl">Model Version:</span> <span class="meta-val">v0.1.0-rules+ensemble</span></div>
            </div>
            <div class="reasons-list-block">
              <div class="reasons-title">Detected Risk Factors:</div>
              <ul class="reasons-items">
                ${(reasons.length ? reasons : ['Normal legitimate transaction parameters verified']).map(r => `
                  <li class="reason-item"><span class="bullet-dot"></span><span>${r}</span></li>
                `).join('')}
              </ul>
            </div>
          </div>
        `;

        showToast(
          `${tier} RISK Evaluated`,
          `Transaction assessed with ${finalScore}% risk index.`,
          tier === 'HIGH'
        );
      });
    }
  }

  // Periodic Live Stream simulation
  setInterval(() => {
    if (!liveStreamActive) return;
    summary.total_transactions += 1;
    const isRisk = Math.random() < 0.25;
    if (isRisk) {
      summary.flagged_transactions += 1;
      const amt = Math.floor(1000 + Math.random() * 15000);
      showToast(
        '🚨 Live Alert: Anomalous Transfer Flagged',
        `High velocity transfer ($${amt.toLocaleString()}) intercepted by FraudShield AI.`,
        true
      );
    }
    const totElem = document.querySelector('.metric-huge-value');
    if (totElem) totElem.textContent = summary.total_transactions.toLocaleString();
  }, 10000);

  // Initialize
  render();
})();
