import React from 'react';

interface HeaderProps {
  onSignInClick: () => void;
  onGetStartedClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onSignInClick, onGetStartedClick }) => {
  return (
    <header className="landing-navbar">
      <div className="navbar-container">
        {/* Brand Logo */}
        <a href="#home" className="brand-logo-group">
          <div className="logo-shield-wrapper">
            <svg className="shield-icon" viewBox="0 0 44 48" fill="none">
              <path
                d="M22 2 L40 10 C40 30 22 46 22 46 C22 46 4 30 4 10 Z"
                fill="#200407"
                stroke="url(#navShieldGold)"
                strokeWidth="2.5"
              />
              <path
                d="M22 6 L36 12 C36 28 22 41 22 41 C22 41 8 28 8 12 Z"
                stroke="#FF385C"
                strokeWidth="1.2"
                opacity="0.8"
              />
              {/* Glowing Fingerprint inside */}
              <g transform="translate(22, 23) scale(0.38)" stroke="#FFD166" strokeWidth="3" strokeLinecap="round">
                <path d="M-6 10 C -6 -4, 6 -4, 6 10" />
                <path d="M0 12 L0 2" />
                <path d="M-13 14 C -13 -10, 13 -10, 13 14" />
                <path d="M-20 18 C -20 -16, 20 -16, 20 18" />
                <path d="M-26 22 C -26 -22, 26 -22, 26 22" />
              </g>
              <defs>
                <linearGradient id="navShieldGold" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFE066" />
                  <stop offset="100%" stopColor="#D97706" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="brand-text-col">
            <div className="brand-title">
              FraudShield <span className="gold-accent">AI</span>
            </div>
            <div className="brand-tagline">Secure Today. Safer Tomorrow.</div>
          </div>
        </a>

        {/* Navigation Links */}
        <nav className="nav-links">
          <a href="#home" className="nav-link active">Home</a>
          <a href="#features" className="nav-link">Features</a>
          <a href="#solutions" className="nav-link">Solutions</a>
          <a href="#technology" className="nav-link">Technology</a>
          <a href="#use-cases" className="nav-link">Use Cases</a>
          <a href="#about" className="nav-link">About</a>
          <a href="#contact" className="nav-link">Contact</a>
        </nav>

        {/* Action Buttons */}
        <div className="nav-actions">
          <button className="btn btn-outline signin-btn" onClick={onSignInClick}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Sign In
          </button>
          <button className="btn btn-gold getstarted-btn" onClick={onGetStartedClick}>
            Get Started
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};
