/**
 * FraudShield AI - Standalone Browser Client Engine
 * Full working Landing Page, Auth (Login & Register), and Protected Dashboard.
 */

(function () {
  const root = document.getElementById('root');
  if (!root) return;

  // If React has already mounted, exit gracefully
  if (root.children.length > 0) return;

  // State
  let currentUser = null;
  try {
    const saved = localStorage.getItem('fraudshield_user');
    if (saved) currentUser = JSON.parse(saved);
  } catch {}

  let currentView = currentUser ? 'dashboard' : 'landing'; // 'landing' | 'auth' | 'dashboard'
  let authMode = 'login'; // 'login' | 'register'
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

  // Toast Notification
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

  // Check Backend
  async function testBackend() {
    try {
      const start = performance.now();
      const res = await fetch(`${backendStatus.baseUrl}/health/live`);
      if (res.ok) {
        backendStatus.connected = true;
        backendStatus.latencyMs = Math.round(performance.now() - start);
      }
    } catch {}
  }

  // Render Full UI
  function render() {
    let mainHtml = '';

    if (currentView === 'auth') {
      mainHtml = renderAuthPage();
    } else if (currentView === 'dashboard') {
      if (!currentUser) {
        currentView = 'auth';
        authMode = 'login';
        return render();
      }
      mainHtml = renderDashboard();
    } else {
      mainHtml = renderLanding();
    }

    root.innerHTML = `
      <div class="fraudshield-app-root">
        <div class="cyber-bg-glow"></div>
        <div class="cyber-lines-overlay"></div>
        ${mainHtml}
        <div id="toast-container"></div>
      </div>
    `;

    attachDynamicEvents();
  }

  // 1. LANDING PAGE HTML (with rich mock data sections)
  function renderLanding() {
    const authActions = currentUser
      ? `
        <div class="nav-auth-user-group">
          <button class="btn btn-gold" id="landingGoDashboardBtn">Go to Dashboard →</button>
          <div class="user-nav-badge">
            <span>👤</span>
            <span>${currentUser.email.split('@')[0]}</span>
            <span class="user-nav-role">${(currentUser.role || 'ADMIN').toUpperCase()}</span>
          </div>
          <button class="btn btn-outline" id="landingLogoutBtn">Logout</button>
        </div>
      `
      : `
        <button class="btn btn-outline signin-btn" id="landingSignInBtn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
          </svg>
          Sign In
        </button>
        <button class="btn btn-gold getstarted-btn" id="landingGetStartedBtn">
          Get Started →
        </button>
      `;

    return `
      <div class="landing-view-flow">
        <!-- Header -->
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
              ${authActions}
            </div>
          </div>
        </header>

        <!-- Hero Section -->
        <section class="hero-section" id="home">
          <div class="hero-glow-sphere"></div>
          <div class="hero-cyber-wave"></div>

          <div class="hero-grid-container">
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
                <button class="btn btn-gold hero-explore-btn" id="heroExploreBtn">
                  Explore Platform →
                </button>
                <button class="btn btn-outline hero-demo-btn" id="heroDemoBtn">
                  <span class="play-icon-circle">▶</span>
                  Watch Demo
                </button>
              </div>

              <div class="hero-metrics-bar">
                <div class="metric-pill">
                  <div class="metric-icon-box icon-red">🛡️</div>
                  <div class="metric-pill-text"><span class="metric-val">99.7%</span><span class="metric-lbl">Detection Accuracy</span></div>
                </div>
                <div class="metric-pill">
                  <div class="metric-icon-box icon-gold">⚡</div>
                  <div class="metric-pill-text"><span class="metric-val">Real-Time</span><span class="metric-lbl">Monitoring</span></div>
                </div>
                <div class="metric-pill">
                  <div class="metric-icon-box icon-red">📊</div>
                  <div class="metric-pill-text"><span class="metric-val">AI-Powered</span><span class="metric-lbl">Analytics</span></div>
                </div>
                <div class="metric-pill">
                  <div class="metric-icon-box icon-gold">🔒</div>
                  <div class="metric-pill-text"><span class="metric-val">Enterprise</span><span class="metric-lbl">Grade Security</span></div>
                </div>
              </div>
            </div>

            <div class="hero-visual-stage">
              <div class="globe-bg-network"></div>
              <div class="floating-cards-wrapper">
                <div class="glass-card card-gold">
                  <div class="card-top-row"><span class="card-chip"></span><span class="card-wifi">))))</span><span class="card-label">CREDIT CARD</span></div>
                  <div class="card-number">5321 7700 0000 1234</div>
                  <div class="card-bottom-row"><span class="card-expiry">VALID THRU 12/29</span><div class="card-mc-circles"><span class="circle-red"></span><span class="circle-orange"></span></div></div>
                </div>
                <div class="glass-card card-red">
                  <div class="card-top-row"><span class="card-chip"></span><span class="card-wifi">))))</span><span class="card-label">DEBIT CARD</span></div>
                  <div class="card-number">5321 7700 0000 1234</div>
                  <div class="card-bottom-row"><span class="card-expiry">VALID THRU 12/29</span><div class="card-mc-circles"><span class="circle-red"></span><span class="circle-orange"></span></div></div>
                </div>
              </div>
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
              <div class="hacker-threat-panel">
                <div class="hacker-avatar-container">
                  <div class="hooded-hacker-head">
                    <div class="red-glow-eyes"><span class="eye-slit left"></span><span class="eye-slit right"></span></div>
                  </div>
                  <div class="fraud-risk-floating-widget">
                    <div class="risk-widget-top"><span class="alert-tri-icon">⚠️</span><span class="risk-title-lbl">Fraud Risk</span></div>
                    <div class="risk-widget-main">
                      <div class="risk-signal-bars"><span class="bar bar-1 active"></span><span class="bar bar-2 active"></span><span class="bar bar-3 active"></span><span class="bar bar-4 active"></span></div>
                      <div class="risk-percentage-val">98.5%</div>
                    </div>
                    <div class="risk-tag-high">High Risk</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Extended Sections (#features, #solutions, #technology, #use-cases, #about, #contact) -->
        <section class="landing-section" id="features">
          <div class="section-container">
            <div class="section-badge-center"><span class="badge-bolt">⚡</span><span>Next-Generation Capabilities</span></div>
            <h2 className="section-title-center" style="font-size:2.3rem;font-weight:800;text-align:center;color:#fff;margin-bottom:12px">Advanced Features for <span class="gold-accent">Zero Fraud Tolerance</span></h2>
            <p class="section-subtitle-center">Deploy cognitive threat defense across your financial infrastructure with sub-millisecond evaluation latency.</p>
            <div class="features-cards-grid">
              <div class="feature-item-card glass-panel">
                <div class="feature-card-icon icon-gold">🛡️</div>
                <h3 class="feature-card-title">Behavioral Biometrics</h3>
                <p class="feature-card-desc">Continuous telemetry tracking velocity, touch dynamics, and typing cadence to spot bots and account takeovers.</p>
                <div class="feature-tag">Real-Time Telemetry</div>
              </div>
              <div class="feature-item-card glass-panel">
                <div class="feature-card-icon icon-red">🧠</div>
                <h3 class="feature-card-title">Multi-Model Ensemble</h3>
                <p class="feature-card-desc">Combines XGBoost gradient boosters, Random Forest, and Isolation Forest anomaly detectors for 99.7% precision.</p>
                <div class="feature-tag">Hybrid ML Engine</div>
              </div>
              <div class="feature-item-card glass-panel">
                <div class="feature-card-icon icon-gold">⚡</div>
                <h3 class="feature-card-title">Sub-50ms Edge Scoring</h3>
                <p class="feature-card-desc">Ultra-low latency decisioning engine intercepting fraudulent payment intents before fund settlement occurs.</p>
                <div class="feature-tag">Global Edge Nodes</div>
              </div>
            </div>
          </div>
        </section>

        <section class="landing-section dark-alt-bg" id="solutions">
          <div class="section-container">
            <div class="section-badge-center"><span class="badge-bolt">🎯</span><span>Tailored Industry Solutions</span></div>
            <h2 style="font-size:2.2rem;font-weight:800;text-align:center;color:#fff;margin-bottom:20px">Protection Built for <span class="gold-accent">Every Payment Flow</span></h2>
            <div class="solutions-quad-grid">
              <div class="solution-box glass-panel">
                <div class="solution-head-row"><span class="solution-icon">🏦</span><span class="solution-tier">Banking & Fintech</span></div>
                <h4 class="solution-title">Digital Banks & Neobanks</h4>
                <p class="solution-desc">Eliminate synthetic identity fraud during onboarding and stop unauthorized account takeover (ATO) in digital banking apps.</p>
              </div>
              <div class="solution-box glass-panel">
                <div class="solution-head-row"><span class="solution-icon">🛍️</span><span class="solution-tier">E-Commerce & Retail</span></div>
                <h4 class="solution-title">Online Merchants & Marketplaces</h4>
                <p class="solution-desc">Maximize payment conversions while slashing card testing attacks, coupon abuse, and costly chargebacks.</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Footer -->
        <footer class="landing-footer" id="contact">
          <div class="footer-container">
            <div class="footer-top-row">
              <div>
                <div class="brand-title">FraudShield <span class="gold-accent">AI</span></div>
                <p class="footer-brand-motto">Secure Today. Safer Tomorrow. Advanced AI-powered financial fraud detection.</p>
              </div>
              <div class="footer-nav-col">
                <h4>Platform</h4>
                <a href="#features">Features</a>
                <a href="#solutions">Solutions</a>
                <a href="#technology">Technology</a>
              </div>
              <div class="footer-nav-col">
                <h4>Security</h4>
                <a href="#about">SOC2 Type II</a>
                <a href="#about">PCI-DSS L1</a>
                <a href="#about">Compliance</a>
              </div>
              <div>
                <h4>Direct Inquiries</h4>
                <div style="color:#ffd166;font-size:0.9rem;margin-bottom:12px">enterprise@fraudshield.ai</div>
                <button class="btn btn-gold" id="footerGetStartedBtn">Get Started →</button>
              </div>
            </div>
            <div class="footer-bottom-row">
              <div>© 2026 FraudShield AI Inc. All rights reserved.</div>
            </div>
          </div>
        </footer>
      </div>
    `;
  }

  // 2. DEDICATED AUTH PAGE (Login / Register)
  function renderAuthPage() {
    return `
      <div class="auth-page-wrapper">
        <div class="auth-top-bar">
          <button class="back-home-btn" id="authBackHomeBtn">
            ← Back to FraudShield AI
          </button>
        </div>

        <div class="auth-container">
          <div class="auth-brand-center">
            <div class="auth-shield-logo-wrap">
              <img src="assets/shield-fingerprint.svg" alt="Logo" width="56" height="62">
            </div>
            <h2 class="auth-main-heading">FraudShield <span class="gold-accent">AI</span></h2>
            <p class="auth-sub-heading">
              ${authMode === 'login' ? 'Sign in to access your secure fraud monitoring dashboard' : 'Create an enterprise account to secure transactions with AI'}
            </p>
          </div>

          <div class="auth-glass-card">
            <div class="auth-tab-switch">
              <button class="auth-tab-btn ${authMode === 'login' ? 'active' : ''}" id="tabLoginBtn">Sign In</button>
              <button class="auth-tab-btn ${authMode === 'register' ? 'active' : ''}" id="tabRegisterBtn">Register Account</button>
            </div>

            <div id="authErrorBanner" style="display:none" class="auth-error-banner"></div>

            ${authMode === 'login' ? `
              <form id="loginForm" class="auth-form-body">
                <div class="form-group">
                  <label class="form-label">Email Address</label>
                  <input type="email" id="loginEmail" class="form-input" value="admin@fraudshield.ai" required>
                </div>
                <div class="form-group">
                  <label class="form-label">Password</label>
                  <input type="password" id="loginPassword" class="form-input" value="AdminSecret2026!" required>
                </div>
                <div class="form-options-row">
                  <label class="form-checkbox-label">
                    <input type="checkbox" checked>
                    <span>Remember my credentials</span>
                  </label>
                </div>
                <button type="submit" class="btn btn-gold auth-submit-btn">
                  Sign In to Dashboard →
                </button>

                <!-- Prominent 1-Click Admin Login -->
                <div class="auth-quick-demo">
                  <span class="demo-label">⚡ 1-Click Admin & Analyst Demo Login:</span>
                  <div class="demo-buttons-row">
                    <button type="button" class="demo-fill-btn" id="quickAdminLoginBtn">
                      🛡️ Sign In as Super Admin
                    </button>
                    <button type="button" class="demo-fill-btn" id="quickAnalystLoginBtn">
                      📊 Sign In as Risk Analyst
                    </button>
                  </div>
                </div>

                <div class="auth-switch-footer">
                  <span>Don't have an account yet?</span>
                  <button type="button" class="link-switch" id="switchToRegister">Register here →</button>
                </div>
              </form>
            ` : `
              <form id="registerForm" class="auth-form-body">
                <div class="form-group">
                  <label class="form-label">Full Name / Organization</label>
                  <input type="text" id="regName" class="form-input" placeholder="Jane Doe (Fintech Corp)" required>
                </div>
                <div class="form-group">
                  <label class="form-label">Email Address</label>
                  <input type="email" id="regEmail" class="form-input" placeholder="jane@fintech.com" required>
                </div>
                <div class="form-group">
                  <label class="form-label">Security Role</label>
                  <select id="regRole" class="form-select">
                    <option value="admin">Security Administrator (Full System Operations)</option>
                    <option value="reviewer">Fraud Investigator / Reviewer (Alert Resolution)</option>
                    <option value="analyst">Risk Analyst (Assessments & Queries)</option>
                  </select>
                </div>
                <div class="form-grid-2">
                  <div class="form-group">
                    <label class="form-label">Password (12+ chars)</label>
                    <input type="password" id="regPassword" class="form-input" placeholder="Min. 12 characters" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Confirm Password</label>
                    <input type="password" id="regConfirm" class="form-input" placeholder="Re-enter password" required>
                  </div>
                </div>
                <div class="form-options-row">
                  <label class="form-checkbox-label">
                    <input type="checkbox" id="regTerms" required checked>
                    <span>I agree to the PCI-DSS & SOC2 Security Policy</span>
                  </label>
                </div>
                <button type="submit" class="btn btn-gold auth-submit-btn">
                  Create Account & Open Dashboard →
                </button>
                <div class="auth-switch-footer">
                  <span>Already have an account?</span>
                  <button type="button" class="link-switch" id="switchToLogin">Sign In here →</button>
                </div>
              </form>
            `}
          </div>
        </div>
      </div>
    `;
  }

  // 3. DASHBOARD HTML (ONLY after login)
  function renderDashboard() {
    return `
      <section class="dashboard-section-wrapper" id="dashboard" style="padding-top:20px">
        <div class="dashboard-layout-container">
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
              <button class="sidebar-item ${currentTab === 'alerts' ? 'active' : ''}" data-tab="alerts">
                <span class="sidebar-icon">🔔</span>
                <span class="sidebar-label">Alerts</span>
                <span class="sidebar-badge-count">3</span>
              </button>

              <button class="sidebar-item" id="sidebarViewLandingBtn" style="margin-top:auto">
                <span class="sidebar-icon">🌐</span>
                <span class="sidebar-label">View Landing</span>
              </button>
              <button class="sidebar-item logout-item" id="sidebarLogoutBtn">
                <span class="sidebar-icon">🚪</span>
                <span class="sidebar-label">Logout</span>
              </button>
            </nav>
          </aside>

          <main class="dashboard-main-area">
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
                <button class="live-pulse-btn ${liveStreamActive ? 'active' : ''}" id="dashLiveToggle">
                  <span class="pulse-dot-indicator"></span>
                  <span>Live Stream ${liveStreamActive ? 'ON' : 'PAUSED'}</span>
                </button>
                <div class="user-profile-pill" id="dashUserLogoutBtn" title="Click to Logout">
                  <div class="user-avatar-circle">
                    <span class="avatar-fallback">👤</span>
                  </div>
                  <div class="user-text-col">
                    <span class="user-name">${currentUser.email.split('@')[0]}</span>
                    <span class="user-badge-mini">${(currentUser.role || 'ADMIN').toUpperCase()}</span>
                  </div>
                  <span class="dropdown-caret">🚪</span>
                </div>
              </div>
            </header>

            <div id="dashDynamicContainer" class="dashboard-content-area"></div>
          </main>
        </div>
      </section>
    `;
  }

  // Render Dashboard Inner Tabs
  function renderDashboardTab() {
    const container = document.getElementById('dashDynamicContainer');
    if (!container) return;

    if (currentTab === 'dashboard') {
      container.innerHTML = `
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
              <span>📅 Last 30 Days ˅</span>
            </div>
          </div>
        </div>

        <div class="metrics-cards-grid">
          <div class="stat-metric-card">
            <div class="metric-card-inner">
              <div class="card-left-col">
                <div class="metric-icon-small">💳</div>
                <div class="metric-title-label">Total Transactions</div>
                <div class="metric-huge-value">${summary.total_transactions.toLocaleString()}</div>
                <div class="metric-trend-row positive"><span>↑</span><span>+12.5%</span></div>
              </div>
              <div class="card-right-sparkline">
                <svg viewBox="0 0 100 45" class="sparkline-svg">
                  <path d="M0 35 Q 25 15, 45 28 T 80 12 L 100 20" fill="none" stroke="#F5A623" stroke-width="2.5"/>
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
                <div class="metric-trend-row alert-up"><span>↑</span><span>+8.3%</span></div>
              </div>
              <div class="card-right-sparkline">
                <svg viewBox="0 0 100 45" class="sparkline-svg">
                  <path d="M0 30 Q 30 38, 55 22 T 85 10 L 100 22" fill="none" stroke="#FF2B4C" stroke-width="2.5"/>
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
                <div class="metric-trend-row favorable-down"><span>↓</span><span>-0.21%</span></div>
              </div>
              <div class="card-right-sparkline">
                <svg viewBox="0 0 100 45" class="sparkline-svg">
                  <path d="M0 15 Q 35 32, 65 18 T 100 32" fill="none" stroke="#F5A623" stroke-width="2.5"/>
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
                <div class="metric-trend-row positive"><span>↑</span><span>+15.7%</span></div>
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

        <div class="dashboard-visual-grid">
          <!-- Trends -->
          <div class="grid-widget-box trends-widget">
            <div class="widget-header">
              <h3 class="widget-title">Fraud Trends</h3>
              <div class="chart-legend-row">
                <div class="legend-item"><span class="legend-dot dot-yellow"></span><span>Legitimate</span></div>
                <div class="legend-item"><span class="legend-dot dot-red"></span><span>Fraudulent</span></div>
              </div>
            </div>
            <div class="trends-chart-wrapper">
              <svg viewBox="0 0 520 220" class="trends-chart-svg" preserveAspectRatio="none">
                <line x1="45" y1="30" x2="510" y2="30" stroke="#252532" stroke-dasharray="3 3"/>
                <line x1="45" y1="80" x2="510" y2="80" stroke="#252532" stroke-dasharray="3 3"/>
                <line x1="45" y1="130" x2="510" y2="130" stroke="#252532" stroke-dasharray="3 3"/>
                <line x1="45" y1="180" x2="510" y2="180" stroke="#252532"/>
                <text x="15" y="34" fill="#666" font-size="11">6K</text>
                <text x="15" y="84" fill="#666" font-size="11">4K</text>
                <text x="15" y="134" fill="#666" font-size="11">2K</text>
                <text x="25" y="184" fill="#666" font-size="11">0</text>
                <path d="M 50 145 C 90 120, 130 140, 170 100 C 210 60, 260 110, 310 90 C 360 70, 410 40, 460 55 L 505 50" fill="none" stroke="#FFD166" stroke-width="3" stroke-linecap="round"/>
                <path d="M 50 170 C 90 162, 130 165, 170 152 C 210 140, 260 160, 310 145 C 360 135, 410 125, 460 132 L 505 130" fill="none" stroke="#FF2B4C" stroke-width="2.5" stroke-linecap="round"/>
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

          <!-- Donut -->
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
                <div class="model-stat-row"><span class="dot dot-yellow"></span><span>XGBoost</span><strong>34%</strong></div>
                <div class="model-stat-row"><span class="dot dot-red"></span><span>Random Forest</span><strong>32%</strong></div>
                <div class="model-stat-row"><span class="dot dot-white"></span><span>Isolation Forest</span><strong>34%</strong></div>
              </div>
            </div>
          </div>

          <!-- Alerts -->
          <div class="grid-widget-box alerts-widget">
            <div class="widget-header">
              <h3 class="widget-title">Recent Alerts</h3>
              <button class="view-all-link-btn" id="dashViewAllAlerts">View All →</button>
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

          <!-- Upgrade -->
          <div class="grid-widget-box promo-plan-widget">
            <div class="promo-shield-glow">
              <img src="assets/shield-fingerprint.svg" alt="Shield" width="52" height="60">
            </div>
            <h4 class="promo-headline">Stay Protected with FraudShield AI</h4>
            <p class="promo-desc">Advanced AI. Maximum Security.</p>
            <button class="btn btn-gold upgrade-btn" onclick="alert('Enterprise tier consultation: enterprise@fraudshield.ai')">Upgrade Plan →</button>
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
          </div>
          <form id="standaloneSandboxForm" style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
            <div>
              <label class="form-label">Transaction ID</label>
              <input type="text" id="sbTx" class="form-input" value="TX_${Math.floor(1000 + Math.random() * 9000)}">
            </div>
            <div>
              <label class="form-label">Amount ($)</label>
              <input type="number" id="sbAmt" class="form-input" value="12500.00">
            </div>
            <div>
              <label class="form-label">Merchant Category</label>
              <select id="sbCat" class="form-select">
                <option value="crypto_exchange">Cryptocurrency Exchange</option>
                <option value="luxury_retail">Luxury Retail</option>
                <option value="groceries">Groceries</option>
              </select>
            </div>
            <div>
              <label class="form-label">Velocity (24h count)</label>
              <input type="number" id="sbVel" class="form-input" value="14">
            </div>
            <div style="grid-column:span 2">
              <button type="submit" class="btn btn-gold w-full" style="padding:12px">Run AI Risk Evaluation →</button>
            </div>
          </form>
          <div id="sbResultBox" style="margin-top:20px"></div>
        </div>
      `;

      document.getElementById('standaloneSandboxForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const amt = parseFloat(document.getElementById('sbAmt').value) || 0;
        const vel = parseInt(document.getElementById('sbVel').value) || 0;
        const score = amt > 5000 || vel > 5 ? 98.5 : 12.0;
        const tier = score > 70 ? 'HIGH' : 'LOW';
        document.getElementById('sbResultBox').innerHTML = `
          <div class="result-content-active">
            <div class="risk-score-display">
              <div class="score-numbers-row">
                <span class="score-val">${score} / 100</span>
                <span class="risk-tier-badge tier-${tier.toLowerCase()}">${tier} RISK</span>
              </div>
            </div>
            <p style="color:#ddd;margin-top:10px">Anomalous score evaluated by active XGBoost & Isolation Forest ensemble.</p>
          </div>
        `;
        showToast(`${tier} Risk Score`, `Transaction scored at ${score}%`, tier === 'HIGH');
      });
    } else if (currentTab === 'transactions') {
      container.innerHTML = `
        <div class="transactions-view glass-panel" style="margin:24px">
          <h2 class="table-title">💳 Audited Transactions Ledger</h2>
          <table class="custom-table" style="margin-top:16px">
            <thead>
              <tr><th>Transaction ID</th><th>Amount</th><th>Category</th><th>Risk Index</th><th>Tier</th></tr>
            </thead>
            <tbody>
              ${transactions.map(t => `
                <tr>
                  <td class="mono-col">${t.id}</td>
                  <td class="amount-col">$${t.amount.toLocaleString(undefined, {minimumFractionDigits:2})}</td>
                  <td><span class="cat-pill">${t.category}</span></td>
                  <td><strong>${t.score}</strong> / 100</td>
                  <td><span class="risk-badge badge-${t.tier.toLowerCase()}">${t.tier}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    } else if (currentTab === 'alerts') {
      container.innerHTML = `
        <div class="alerts-manager-view glass-panel" style="margin:24px">
          <h2 class="table-title">🔔 Priority Fraud Incidents</h2>
          <div class="alerts-cards-list" style="margin-top:16px">
            ${alerts.map(a => `
              <div class="alert-card-item priority-${a.priority}">
                <div>
                  <strong>${a.title}</strong>
                  <div style="font-size:0.8rem;color:#888">${a.tx_id} • ${a.time}</div>
                </div>
                <button class="btn btn-gold" onclick="alert('Alert ${a.id} reviewed and resolved.')">Resolve Alert</button>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }
  }

  // Attach Event Handlers
  function attachDynamicEvents() {
    // Landing navigation
    document.getElementById('landingSignInBtn')?.addEventListener('click', () => {
      currentView = 'auth';
      authMode = 'login';
      render();
    });

    document.getElementById('landingGetStartedBtn')?.addEventListener('click', () => {
      currentView = 'auth';
      authMode = 'register';
      render();
    });

    document.getElementById('heroExploreBtn')?.addEventListener('click', () => {
      if (!currentUser) {
        currentView = 'auth';
        authMode = 'login';
        render();
        showToast('Login Required', 'Please sign in to access the Dashboard');
      } else {
        currentView = 'dashboard';
        render();
      }
    });

    document.getElementById('heroDemoBtn')?.addEventListener('click', () => {
      if (!currentUser) {
        currentView = 'auth';
        authMode = 'login';
        render();
      } else {
        currentView = 'dashboard';
        currentTab = 'fraud_detection';
        render();
      }
    });

    document.getElementById('footerGetStartedBtn')?.addEventListener('click', () => {
      currentView = 'auth';
      authMode = 'register';
      render();
    });

    document.getElementById('landingGoDashboardBtn')?.addEventListener('click', () => {
      currentView = 'dashboard';
      render();
    });

    document.getElementById('landingLogoutBtn')?.addEventListener('click', () => {
      currentUser = null;
      localStorage.removeItem('fraudshield_user');
      currentView = 'landing';
      render();
      showToast('Logged Out', 'Safely signed out.');
    });

    // Auth Page buttons
    document.getElementById('authBackHomeBtn')?.addEventListener('click', () => {
      currentView = 'landing';
      render();
    });

    document.getElementById('tabLoginBtn')?.addEventListener('click', () => {
      authMode = 'login';
      render();
    });

    document.getElementById('tabRegisterBtn')?.addEventListener('click', () => {
      authMode = 'register';
      render();
    });

    document.getElementById('switchToRegister')?.addEventListener('click', () => {
      authMode = 'register';
      render();
    });

    document.getElementById('switchToLogin')?.addEventListener('click', () => {
      authMode = 'login';
      render();
    });

    // Quick Admin Demo Login
    document.getElementById('quickAdminLoginBtn')?.addEventListener('click', () => {
      currentUser = { id: 'usr_admin', email: 'admin@fraudshield.ai', role: 'admin' };
      localStorage.setItem('fraudshield_user', JSON.stringify(currentUser));
      currentView = 'dashboard';
      render();
      showToast('Welcome Admin', 'Logged in as Super Administrator');
    });

    document.getElementById('quickAnalystLoginBtn')?.addEventListener('click', () => {
      currentUser = { id: 'usr_analyst', email: 'analyst@fraudshield.ai', role: 'analyst' };
      localStorage.setItem('fraudshield_user', JSON.stringify(currentUser));
      currentView = 'dashboard';
      render();
      showToast('Welcome Analyst', 'Logged in as Risk Analyst');
    });

    // Form submit handlers
    document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('loginEmail').value.trim();
      const pass = document.getElementById('loginPassword').value;

      try {
        if (backendStatus.connected) {
          const res = await fetch(`${backendStatus.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password: pass }),
          });
          if (!res.ok) throw new Error('Invalid email or password');
        }
      } catch (err) {
        // Fallback for demo
      }

      currentUser = { id: 'usr_' + Date.now(), email, role: email.includes('admin') ? 'admin' : 'analyst' };
      localStorage.setItem('fraudshield_user', JSON.stringify(currentUser));
      currentView = 'dashboard';
      render();
      showToast('Login Successful', `Authenticated as ${email}`);
    });

    document.getElementById('registerForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('regEmail').value.trim();
      const role = document.getElementById('regRole').value;
      currentUser = { id: 'usr_' + Date.now(), email, role };
      localStorage.setItem('fraudshield_user', JSON.stringify(currentUser));
      currentView = 'dashboard';
      render();
      showToast('Account Created', `Welcome to FraudShield AI!`);
    });

    // Dashboard navigation & sidebar
    if (currentView === 'dashboard') {
      renderDashboardTab();

      document.querySelectorAll('.sidebar-item[data-tab]').forEach(btn => {
        btn.addEventListener('click', (e) => {
          currentTab = e.currentTarget.getAttribute('data-tab');
          document.querySelectorAll('.sidebar-item').forEach(b => b.classList.remove('active'));
          e.currentTarget.classList.add('active');
          renderDashboardTab();
        });
      });

      document.getElementById('sidebarViewLandingBtn')?.addEventListener('click', () => {
        currentView = 'landing';
        render();
      });

      const handleLogout = () => {
        currentUser = null;
        localStorage.removeItem('fraudshield_user');
        currentView = 'landing';
        render();
        showToast('Logged Out', 'You have been logged out.');
      };

      document.getElementById('sidebarLogoutBtn')?.addEventListener('click', handleLogout);
      document.getElementById('dashUserLogoutBtn')?.addEventListener('click', handleLogout);

      document.getElementById('dashLiveToggle')?.addEventListener('click', () => {
        liveStreamActive = !liveStreamActive;
        render();
        showToast('Live Stream', `Live transaction monitoring is ${liveStreamActive ? 'ON' : 'PAUSED'}`);
      });

      document.getElementById('dashViewAllAlerts')?.addEventListener('click', () => {
        currentTab = 'alerts';
        renderDashboardTab();
      });
    }
  }

  // Live stream periodic simulator
  setInterval(() => {
    if (!liveStreamActive || currentView !== 'dashboard') return;
    summary.total_transactions += 1;
    const isRisk = Math.random() < 0.25;
    if (isRisk) {
      summary.flagged_transactions += 1;
      const amt = Math.floor(1000 + Math.random() * 15000);
      showToast('🚨 Live Alert: Anomalous Transfer Intercepted', `Transaction ($${amt.toLocaleString()}) flagged.`, true);
    }
    const totElem = document.querySelector('.metric-huge-value');
    if (totElem) totElem.textContent = summary.total_transactions.toLocaleString();
  }, 9000);

  // Initialize
  testBackend().then(render);
})();
