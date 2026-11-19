import React from 'react';

interface HeroProps {
  onExplorePlatform: () => void;
  onWatchDemo: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onExplorePlatform, onWatchDemo }) => {
  return (
    <section className="hero-section" id="home">
      {/* Background Cyber Glowing Ribbons & Sphere */}
      <div className="hero-glow-sphere" />
      <div className="hero-cyber-wave" />

      <div className="hero-grid-container">
        {/* Left Column: Headline, Description & Badges */}
        <div className="hero-left-content">
          {/* Badge */}
          <div className="hero-badge">
            <span className="badge-bolt">⚡</span>
            <span className="badge-text">AI-Powered Financial Security</span>
          </div>

          {/* Main Titles */}
          <h1 className="hero-title">
            FraudShield <span className="gold-text">AI</span>
          </h1>
          <h2 className="hero-subtitle">
            Smart Fraud Detection. Safer Transactions.
          </h2>

          <p className="hero-description">
            Detect, analyze, and prevent financial fraud with advanced machine learning,
            predictive analytics, and real-time monitoring.
          </p>

          {/* CTA Buttons */}
          <div className="hero-cta-group">
            <button className="btn btn-gold hero-explore-btn" onClick={onExplorePlatform}>
              Explore Platform
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>

            <button className="btn btn-outline hero-demo-btn" onClick={onWatchDemo}>
              <span className="play-icon-circle">▶</span>
              Watch Demo
            </button>
          </div>

          {/* 4 Feature Value Badges (Matching the exact mockup) */}
          <div className="hero-metrics-bar">
            {/* Metric 1 */}
            <div className="metric-pill">
              <div className="metric-icon-box icon-red">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF4D4D" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <div className="metric-pill-text">
                <span className="metric-val">99.7%</span>
                <span className="metric-lbl">Detection Accuracy</span>
              </div>
            </div>

            {/* Metric 2 */}
            <div className="metric-pill">
              <div className="metric-icon-box icon-gold">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFD166" strokeWidth="2">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
              </div>
              <div className="metric-pill-text">
                <span className="metric-val">Real-Time</span>
                <span className="metric-lbl">Monitoring</span>
              </div>
            </div>

            {/* Metric 3 */}
            <div className="metric-pill">
              <div className="metric-icon-box icon-red">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF5252" strokeWidth="2">
                  <rect x="3" y="12" width="4" height="9" rx="1" />
                  <rect x="10" y="7" width="4" height="14" rx="1" />
                  <rect x="17" y="3" width="4" height="18" rx="1" />
                </svg>
              </div>
              <div className="metric-pill-text">
                <span className="metric-val">AI-Powered</span>
                <span className="metric-lbl">Analytics</span>
              </div>
            </div>

            {/* Metric 4 */}
            <div className="metric-pill">
              <div className="metric-icon-box icon-gold">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFD166" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </div>
              <div className="metric-pill-text">
                <span className="metric-val">Enterprise</span>
                <span className="metric-lbl">Grade Security</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Holographic Stage, 3D Cards, Pedestal Shield & Hacker */}
        <div className="hero-visual-stage">
          {/* Cybernetic Earth Globe Background Grid */}
          <div className="globe-bg-network" />

          {/* Floating Credit & Debit Cards (Left side of stage) */}
          <div className="floating-cards-wrapper">
            {/* Credit Card Gold */}
            <div className="glass-card card-gold">
              <div className="card-top-row">
                <span className="card-chip" />
                <span className="card-wifi">))))</span>
                <span className="card-label">CREDIT CARD</span>
              </div>
              <div className="card-number">5321 7700 0000 1234</div>
              <div className="card-bottom-row">
                <span className="card-expiry">VALID THRU 12/29</span>
                <div className="card-mc-circles">
                  <span className="circle-red" />
                  <span className="circle-orange" />
                </div>
              </div>
            </div>

            {/* Debit Card Red (Overlapping) */}
            <div className="glass-card card-red">
              <div className="card-top-row">
                <span className="card-chip" />
                <span className="card-wifi">))))</span>
                <span className="card-label">DEBIT CARD</span>
              </div>
              <div className="card-number">5321 7700 0000 1234</div>
              <div className="card-bottom-row">
                <span className="card-expiry">VALID THRU 12/29</span>
                <div className="card-mc-circles">
                  <span className="circle-red" />
                  <span className="circle-orange" />
                </div>
              </div>
            </div>
          </div>

          {/* Central Tiered Golden Pedestal with Holographic Fingerprint Shield */}
          <div className="pedestal-shield-center">
            {/* Holographic Shield */}
            <div className="hologram-shield-float">
              <svg viewBox="0 0 160 190" className="holo-shield-svg">
                <defs>
                  <linearGradient id="heroGoldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#FFF275" />
                    <stop offset="50%" stopColor="#F5A623" />
                    <stop offset="100%" stopColor="#C47D08" />
                  </linearGradient>
                  <filter id="heroShieldGlow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="8" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                {/* Shield Body */}
                <path
                  d="M80 15 L145 42 C145 116 80 175 80 175 C80 175 15 116 15 42 Z"
                  fill="#240306"
                  stroke="url(#heroGoldGradient)"
                  strokeWidth="4"
                  filter="url(#heroShieldGlow)"
                />
                <path
                  d="M80 25 L135 48 C135 110 80 162 80 162 C80 162 25 110 25 48 Z"
                  stroke="#FF2B4C"
                  strokeWidth="1.8"
                  opacity="0.85"
                  fill="none"
                />
                {/* Fingerprint ridges inside */}
                <g transform="translate(80, 95) scale(0.65)" stroke="#FFD166" strokeWidth="3.2" strokeLinecap="round" fill="none">
                  <path d="M-6 12 C -6 -6, 6 -6, 6 12" />
                  <path d="M0 16 L0 4" />
                  <path d="M-15 18 C -15 -14, 15 -14, 15 18" />
                  <path d="M-24 22 C -24 -22, 24 -22, 24 22" />
                  <path d="M-33 26 C -33 -30, 33 -30, 33 26" />
                  <path d="M-42 24 C -42 -38, 42 -38, 42 24" />
                </g>
              </svg>
            </div>

            {/* Glowing Golden Pedestal Platform with Stage Rings */}
            <div className="pedestal-rings-container">
              <div className="ring-disc ring-top" />
              <div className="ring-disc ring-middle" />
              <div className="ring-disc ring-bottom" />
              <div className="stage-light-beam" />
            </div>
          </div>

          {/* Cyber Hacker Silhouette with Glowing Eyes & Risk Monitor (Right side of stage) */}
          <div className="hacker-threat-panel">
            <div className="hacker-avatar-container">
              {/* Silhouette with Glowing Eyes */}
              <div className="hooded-hacker-head">
                <div className="red-glow-eyes">
                  <span className="eye-slit left" />
                  <span className="eye-slit right" />
                </div>
              </div>
              {/* Threat Alert Widget */}
              <div className="fraud-risk-floating-widget">
                <div className="risk-widget-top">
                  <span className="alert-tri-icon">⚠️</span>
                  <span className="risk-title-lbl">Fraud Risk</span>
                </div>
                <div className="risk-widget-main">
                  <div className="risk-signal-bars">
                    <span className="bar bar-1 active" />
                    <span className="bar bar-2 active" />
                    <span className="bar bar-3 active" />
                    <span className="bar bar-4 active" />
                  </div>
                  <div className="risk-percentage-val">98.5%</div>
                </div>
                <div className="risk-tag-high">High Risk</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
