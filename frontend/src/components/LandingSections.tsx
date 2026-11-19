import React, { useState } from 'react';

interface LandingSectionsProps {
  onGetStartedClick: () => void;
  onExploreClick: () => void;
}

export const LandingSections: React.FC<LandingSectionsProps> = ({
  onGetStartedClick,
}) => {
  const [contactName, setContactName] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactCompany, setContactCompany] = useState('');
  const [contactMsg, setContactMsg] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleContactSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setContactName('');
      setContactEmail('');
      setContactCompany('');
      setContactMsg('');
    }, 4000);
  };

  return (
    <div className="landing-extended-sections">
      {/* ===================================================================
          1. FEATURES SECTION (#features)
          =================================================================== */}
      <section className="landing-section" id="features">
        <div className="section-container">
          <div className="section-badge-center">
            <span className="badge-bolt">⚡</span>
            <span>Next-Generation Capabilities</span>
          </div>
          <h2 className="section-title-center">
            Advanced Features Engineered for <span className="gold-accent">Zero Fraud Tolerance</span>
          </h2>
          <p className="section-subtitle-center">
            Deploy cognitive threat defense across your financial infrastructure with sub-millisecond evaluation latency.
          </p>

          <div className="features-cards-grid">
            {/* Feature 1 */}
            <div className="feature-item-card glass-panel">
              <div className="feature-card-icon icon-gold">🛡️</div>
              <h3 className="feature-card-title">Behavioral Biometrics</h3>
              <p className="feature-card-desc">
                Continuous authentication tracking mouse velocity, touch dynamics, gyro motion, and typing cadence to spot bots and account takeover.
              </p>
              <div className="feature-tag">Real-Time Telemetry</div>
            </div>

            {/* Feature 2 */}
            <div className="feature-item-card glass-panel">
              <div className="feature-card-icon icon-red">🧠</div>
              <h3 className="feature-card-title">Multi-Model Ensemble</h3>
              <p className="feature-card-desc">
                Combines XGBoost gradient boosters, Random Forest classifiers, and Isolation Forest anomaly detectors for 99.7% precision.
              </p>
              <div className="feature-tag">Hybrid ML Engine</div>
            </div>

            {/* Feature 3 */}
            <div className="feature-item-card glass-panel">
              <div className="feature-card-icon icon-gold">⚡</div>
              <h3 className="feature-card-title">Sub-50ms Edge Scoring</h3>
              <p className="feature-card-desc">
                Ultra-low latency decisioning engine intercepting fraudulent payment intents before fund settlement occurs.
              </p>
              <div className="feature-tag">Global Edge Nodes</div>
            </div>

            {/* Feature 4 */}
            <div className="feature-item-card glass-panel">
              <div className="feature-card-icon icon-red">📡</div>
              <h3 className="feature-card-title">Consortium Threat Radar</h3>
              <p className="feature-card-desc">
                Cross-merchant threat graph pooling stolen credit card hashes, compromised IPs, and synthetic identities globally.
              </p>
              <div className="feature-tag">Zero-Day Intelligence</div>
            </div>

            {/* Feature 5 */}
            <div className="feature-item-card glass-panel">
              <div className="feature-card-icon icon-gold">⚙️</div>
              <h3 className="feature-card-title">Adaptive Rules Sandbox</h3>
              <p className="feature-card-desc">
                A/B test complex risk velocity rules, custom thresholds, and multi-factor triggers without needing engineering deployments.
              </p>
              <div className="feature-tag">Hot-Reload Policy</div>
            </div>

            {/* Feature 6 */}
            <div className="feature-item-card glass-panel">
              <div className="feature-card-icon icon-red">📑</div>
              <h3 className="feature-card-title">Automated SAR & Compliance</h3>
              <p className="feature-card-desc">
                One-click Suspicious Activity Report (SAR) generation with full cryptographic audit trails compliant with FinCEN and PCI-DSS.
              </p>
              <div className="feature-tag">Regulatory Ready</div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          2. SOLUTIONS SECTION (#solutions)
          =================================================================== */}
      <section className="landing-section dark-alt-bg" id="solutions">
        <div className="section-container">
          <div className="section-badge-center">
            <span className="badge-bolt">🎯</span>
            <span>Tailored Industry Solutions</span>
          </div>
          <h2 className="section-title-center">
            Precision Protection Built for <span className="gold-accent">Every Payment Flow</span>
          </h2>

          <div className="solutions-quad-grid">
            <div className="solution-box glass-panel">
              <div className="solution-head-row">
                <span className="solution-icon">🏦</span>
                <span className="solution-tier">Banking & Fintech</span>
              </div>
              <h4 className="solution-title">Digital Banks & Neobanks</h4>
              <p className="solution-desc">
                Eliminate synthetic identity fraud during onboarding and stop unauthorized account takeover (ATO) in digital banking apps.
              </p>
              <ul className="solution-bullets">
                <li>✓ KYC & AML Screening with biometric liveness</li>
                <li>✓ ACH & Wire Transfer velocity controls</li>
                <li>✓ Mule account clustering and freeze triggers</li>
              </ul>
            </div>

            <div className="solution-box glass-panel">
              <div className="solution-head-row">
                <span className="solution-icon">🛍️</span>
                <span className="solution-tier">E-Commerce & Retail</span>
              </div>
              <h4 className="solution-title">Online Merchants & Marketplaces</h4>
              <p className="solution-desc">
                Maximize payment conversions while slashing card testing attacks, promo coupon abuse, and costly chargeback disputes.
              </p>
              <ul className="solution-bullets">
                <li>✓ Card-Not-Present (CNP) validation</li>
                <li>✓ Frictionless 3D-Secure dynamic step-up</li>
                <li>✓ Friendly fraud dispute automation</li>
              </ul>
            </div>

            <div className="solution-box glass-panel">
              <div className="solution-head-row">
                <span className="solution-icon">🪙</span>
                <span className="solution-tier">Web3 & Digital Assets</span>
              </div>
              <h4 className="solution-title">Crypto Exchanges & On-Ramps</h4>
              <p className="solution-desc">
                Detect high-risk wallet addresses, illicit mixer interaction, and stolen credit card fiat-to-crypto wash trading.
              </p>
              <ul className="solution-bullets">
                <li>✓ Cross-chain taint and wallet scoring</li>
                <li>✓ Instant fiat ramp risk assessment</li>
                <li>✓ Travel Rule compliance workflows</li>
              </ul>
            </div>

            <div className="solution-box glass-panel">
              <div className="solution-head-row">
                <span className="solution-icon">💳</span>
                <span className="solution-tier">Payment Providers</span>
              </div>
              <h4 className="solution-title">Payment Gateways & PSPs</h4>
              <p className="solution-desc">
                Deliver institutional-grade fraud protection as an embedded microservice to all sub-merchants on your processing network.
              </p>
              <ul className="solution-bullets">
                <li>✓ Multi-tenant merchant isolation</li>
                <li>✓ Sub-15ms edge inference REST APIs</li>
                <li>✓ Configurable per-client risk index thresholds</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          3. TECHNOLOGY SECTION (#technology)
          =================================================================== */}
      <section className="landing-section" id="technology">
        <div className="section-container">
          <div className="tech-dual-layout">
            <div className="tech-left-col">
              <div className="hero-badge">
                <span className="badge-bolt">⚙️</span>
                <span className="badge-text">Architecture & AI Stack</span>
              </div>
              <h2 className="section-heading-left">
                How FraudShield AI <span className="gold-accent">Intercepts Fraud</span> in Milliseconds
              </h2>
              <p className="section-paragraph-left">
                Every transaction undergoes real-time feature extraction across 140+ behavioral, network, and biometric vectors before neural graph scoring.
              </p>

              <div className="tech-steps-list">
                <div className="tech-step-item">
                  <div className="step-number-disc">01</div>
                  <div>
                    <h4 className="step-title">Ingestion & Device Fingerprinting</h4>
                    <p className="step-desc">
                      Captures canvas hashes, WebGL profiles, TCP/IP stack fingerprints, and proxy headers within 5 milliseconds.
                    </p>
                  </div>
                </div>

                <div className="tech-step-item">
                  <div className="step-number-disc">02</div>
                  <div>
                    <h4 className="step-title">Graph Linkage & Velocity Evaluation</h4>
                    <p className="step-desc">
                      Instantly cross-references the transaction against our global 4.2B transaction graph to spot syndicate rings.
                    </p>
                  </div>
                </div>

                <div className="tech-step-item">
                  <div className="step-number-disc">03</div>
                  <div>
                    <h4 className="step-title">Ensemble Model Inference</h4>
                    <p className="step-desc">
                      XGBoost and Isolation Forest models yield an explainable 0–100 Risk Index with transparent decision reasons.
                    </p>
                  </div>
                </div>

                <div className="tech-step-item">
                  <div className="step-number-disc">04</div>
                  <div>
                    <h4 className="step-title">Automated Action & Investigator Dispatch</h4>
                    <p className="step-desc">
                      Auto-approves benign charges, triggers biometric 2FA for medium risk, and auto-declines critical fraud alerts.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="tech-right-col">
              {/* Architecture Graphic Box */}
              <div className="architecture-mockup-card glass-panel">
                <div className="arch-card-topbar">
                  <span className="arch-dot red"></span>
                  <span className="arch-dot yellow"></span>
                  <span className="arch-dot green"></span>
                  <span className="arch-title-tag">FraudShield Core Engine v2.4</span>
                </div>
                <div className="arch-pipeline-visual">
                  <div className="pipeline-node node-input">
                    <span className="node-icon">💳</span>
                    <span className="node-text">Transaction Payload</span>
                    <span className="node-time">0.4ms</span>
                  </div>
                  <div className="pipeline-arrow">↓</div>
                  <div className="pipeline-node node-features">
                    <span className="node-icon">⚡</span>
                    <span className="node-text">140+ Feature Extractors</span>
                    <span className="node-time">3.2ms</span>
                  </div>
                  <div className="pipeline-arrow">↓</div>
                  <div className="pipeline-node node-ensemble">
                    <span className="node-icon">🧠</span>
                    <span className="node-text">Hybrid ML Ensemble (XGB + RF + Iso)</span>
                    <span className="node-time">6.8ms</span>
                  </div>
                  <div className="pipeline-arrow">↓</div>
                  <div className="pipeline-node node-decision">
                    <span className="node-icon">🛡️</span>
                    <span className="node-text">Decision: ALLOW | STEP-UP | DECLINE</span>
                    <span className="node-time">Total: 10.4ms</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          4. USE CASES SECTION (#use-cases)
          =================================================================== */}
      <section className="landing-section dark-alt-bg" id="use-cases">
        <div className="section-container">
          <div className="section-badge-center">
            <span className="badge-bolt">📊</span>
            <span>Proven Defense Scenarios</span>
          </div>
          <h2 className="section-title-center">
            Combating Real-World Threats Across the <span className="gold-accent">Digital Economy</span>
          </h2>

          <div className="use-cases-grid">
            <div className="use-case-card glass-panel">
              <div className="uc-badge-tag high">High Impact</div>
              <h3 className="uc-title">Account Takeover (ATO)</h3>
              <p className="uc-desc">
                Attackers using credential stuffing from dark web leaks are intercepted instantly by our behavioral cadence analyzer.
              </p>
              <div className="uc-stat-box">
                <span className="uc-stat-num">99.8%</span>
                <span className="uc-stat-lbl">ATO Attack Prevention Rate</span>
              </div>
            </div>

            <div className="use-case-card glass-panel">
              <div className="uc-badge-tag medium">Card Testing</div>
              <h3 className="uc-title">Card-Not-Present (CNP) Fraud</h3>
              <p className="uc-desc">
                Stops rapid-fire micro-transactions from stolen card syndicates probing validation status on your payment gateways.
              </p>
              <div className="uc-stat-box">
                <span className="uc-stat-num">&lt; 0.02%</span>
                <span className="uc-stat-lbl">False Positive Rate</span>
              </div>
            </div>

            <div className="use-case-card glass-panel">
              <div className="uc-badge-tag high">Syndicates</div>
              <h3 className="uc-title">Synthetic Identity Rings</h3>
              <p className="uc-desc">
                Uncovers fabricated personas mixing real SSNs with fictitious names and addresses before loans or credit lines are drawn.
              </p>
              <div className="uc-stat-box">
                <span className="uc-stat-num">$18.4M+</span>
                <span className="uc-stat-lbl">Monthly Losses Prevented</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          5. ABOUT SECTION (#about)
          =================================================================== */}
      <section className="landing-section" id="about">
        <div className="section-container">
          <div className="about-content-box glass-panel">
            <div className="about-header-row">
              <div className="about-logo-mark">
                <img src="assets/shield-fingerprint.svg" alt="FraudShield AI" width="48" height="54" />
              </div>
              <div>
                <h3 className="about-title">About FraudShield AI</h3>
                <p className="about-sub">Mission-Critical Financial Defense Engineered by Deep Learning Pioneers</p>
              </div>
            </div>

            <div className="about-metrics-bar">
              <div className="about-stat-item">
                <span className="stat-big-number">$4.2B+</span>
                <span className="stat-sub-label">Transactions Audited Safely</span>
              </div>
              <div className="about-stat-item">
                <span className="stat-big-number">99.7%</span>
                <span className="stat-sub-label">Model Detection Accuracy</span>
              </div>
              <div className="about-stat-item">
                <span className="stat-big-number">12.5ms</span>
                <span className="stat-sub-label">Average API Latency</span>
              </div>
              <div className="about-stat-item">
                <span className="stat-big-number">140+</span>
                <span className="stat-sub-label">Countries Monitored 24/7</span>
              </div>
            </div>

            <p className="about-paragraph">
              Founded to build the world's most resilient AI fraud shield, our platform continuously trains on evolving global attack patterns. With dual-head transformer models and real-time behavioral graph analytics, we empower financial institutions, neo-banks, and fast-growing enterprises to transact with absolute certainty.
            </p>
          </div>
        </div>
      </section>

      {/* ===================================================================
          6. CONTACT & INQUIRY SECTION (#contact)
          =================================================================== */}
      <section className="landing-section dark-alt-bg" id="contact">
        <div className="section-container">
          <div className="contact-grid">
            <div className="contact-left-info">
              <div className="hero-badge">
                <span className="badge-bolt">✉️</span>
                <span className="badge-text">Get In Touch</span>
              </div>
              <h2 className="section-heading-left">
                Ready to Secure Your Platform with <span className="gold-accent">FraudShield AI?</span>
              </h2>
              <p className="section-paragraph-left">
                Speak directly with an enterprise solutions architect, request a custom risk simulation benchmark, or configure API sandbox access.
              </p>

              <div className="contact-detail-items">
                <div className="contact-detail-row">
                  <span className="cd-icon">📍</span>
                  <div>
                    <strong>Global Headquarters:</strong>
                    <div>Cyber Security Tower, Financial District</div>
                  </div>
                </div>
                <div className="contact-detail-row">
                  <span className="cd-icon">✉️</span>
                  <div>
                    <strong>Direct Inquiries:</strong>
                    <div className="text-gold">enterprise@fraudshield.ai</div>
                  </div>
                </div>
                <div className="contact-detail-row">
                  <span className="cd-icon">🛡️</span>
                  <div>
                    <strong>Compliance & Security:</strong>
                    <div>SOC2 Type II, PCI-DSS Level 1, ISO 27001 Certified</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="contact-right-form">
              <div className="contact-form-card glass-panel">
                <h3 className="cf-title">Request Enterprise Architecture Demo</h3>
                <p className="cf-sub">Fill out the details below to receive sandbox API access credentials.</p>

                {submitted ? (
                  <div className="contact-success-banner">
                    <span style={{ fontSize: '1.8rem' }}>✅</span>
                    <h4 style={{ color: '#fff', margin: '6px 0' }}>Inquiry Submitted!</h4>
                    <p style={{ color: '#aaa', fontSize: '0.85rem' }}>Our cybersecurity solutions team will contact you within 2 business hours.</p>
                  </div>
                ) : (
                  <form onSubmit={handleContactSubmit}>
                    <div className="form-group">
                      <label className="form-label">Full Name</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="Alex Morgan"
                        value={contactName}
                        onChange={(e) => setContactName(e.target.value)}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Work Email</label>
                      <input
                        type="email"
                        className="form-input"
                        placeholder="alex@fintech.com"
                        value={contactEmail}
                        onChange={(e) => setContactEmail(e.target.value)}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Organization / Monthly Transaction Volume</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="Global Pay Inc. (> 50,000 tx/mo)"
                        value={contactCompany}
                        onChange={(e) => setContactCompany(e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Message / Specific Requirements</label>
                      <textarea
                        className="form-input"
                        rows={3}
                        placeholder="Interested in real-time fraud scoring API and webhook integration..."
                        value={contactMsg}
                        onChange={(e) => setContactMsg(e.target.value)}
                      ></textarea>
                    </div>

                    <button type="submit" className="btn btn-gold w-full" style={{ padding: '12px' }}>
                      Submit Enterprise Demo Request →
                    </button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          FOOTER
          =================================================================== */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-top-row">
            <div className="footer-brand-col">
              <div className="brand-logo-group">
                <div className="logo-shield-wrapper">
                  <img src="assets/shield-fingerprint.svg" alt="FraudShield AI" width="32" height="36" />
                </div>
                <div className="brand-title">FraudShield <span className="gold-accent">AI</span></div>
              </div>
              <p className="footer-brand-motto">
                Secure Today. Safer Tomorrow. Advanced machine learning for real-time financial fraud defense.
              </p>
            </div>

            <div className="footer-nav-col">
              <h4>Platform</h4>
              <a href="#features">Features</a>
              <a href="#solutions">Solutions</a>
              <a href="#technology">Technology</a>
              <a href="#use-cases">Use Cases</a>
            </div>

            <div className="footer-nav-col">
              <h4>Security</h4>
              <a href="#about">Compliance (SOC2/PCI)</a>
              <a href="#about">Encryption Architecture</a>
              <a href="#about">Privacy Shield</a>
              <a href="#about">SAR Automation</a>
            </div>

            <div className="footer-nav-col">
              <h4>Get Started</h4>
              <button className="footer-action-btn" onClick={onGetStartedClick}>
                Create Account →
              </button>
              <div className="cert-badges-row">
                <span className="cert-pill">PCI-DSS L1</span>
                <span className="cert-pill">SOC2 Type II</span>
                <span className="cert-pill">ISO 27001</span>
              </div>
            </div>
          </div>

          <div className="footer-bottom-row">
            <div>© 2026 FraudShield AI Inc. All rights reserved.</div>
            <div className="footer-legal-links">
              <a href="#about">Privacy Policy</a>
              <span>•</span>
              <a href="#about">Terms of Service</a>
              <span>•</span>
              <a href="#about">Security Whitepaper</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
