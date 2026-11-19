import React, { useEffect, useState } from 'react';
import { UserPublic } from '../types/api';

interface HeaderProps {
  currentUser: UserPublic | null;
  onSignInClick: () => void;
  onRegisterClick: () => void;
  onGoToDashboard: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentUser,
  onSignInClick,
  onRegisterClick,
  onGoToDashboard,
  onLogout,
}) => {
  const [activeSection, setActiveSection] = useState('home');
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);

      const sections = ['home', 'features', 'solutions', 'technology', 'use-cases', 'about', 'contact'];
      const scrollPos = window.scrollY + 120;

      for (let i = sections.length - 1; i >= 0; i--) {
        const el = document.getElementById(sections[i]);
        if (el && el.offsetTop <= scrollPos) {
          setActiveSection(sections[i]);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollTo = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
      setActiveSection(id);
    }
  };

  return (
    <header className={`landing-navbar fixed-header ${scrolled ? 'navbar-scrolled' : ''}`}>
      <div className="navbar-container">
        {/* Brand Logo */}
        <a href="#home" onClick={(e) => scrollTo(e, 'home')} className="brand-logo-group">
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

        {/* Navigation Links with Active Scrollspy Highlighting */}
        <nav className="nav-links">
          <a
            href="#home"
            onClick={(e) => scrollTo(e, 'home')}
            className={`nav-link ${activeSection === 'home' ? 'active' : ''}`}
          >
            Home
          </a>
          <a
            href="#features"
            onClick={(e) => scrollTo(e, 'features')}
            className={`nav-link ${activeSection === 'features' ? 'active' : ''}`}
          >
            Features
          </a>
          <a
            href="#solutions"
            onClick={(e) => scrollTo(e, 'solutions')}
            className={`nav-link ${activeSection === 'solutions' ? 'active' : ''}`}
          >
            Solutions
          </a>
          <a
            href="#technology"
            onClick={(e) => scrollTo(e, 'technology')}
            className={`nav-link ${activeSection === 'technology' ? 'active' : ''}`}
          >
            Technology
          </a>
          <a
            href="#use-cases"
            onClick={(e) => scrollTo(e, 'use-cases')}
            className={`nav-link ${activeSection === 'use-cases' ? 'active' : ''}`}
          >
            Use Cases
          </a>
          <a
            href="#about"
            onClick={(e) => scrollTo(e, 'about')}
            className={`nav-link ${activeSection === 'about' ? 'active' : ''}`}
          >
            About
          </a>
          <a
            href="#contact"
            onClick={(e) => scrollTo(e, 'contact')}
            className={`nav-link ${activeSection === 'contact' ? 'active' : ''}`}
          >
            Contact
          </a>
        </nav>

        {/* Action Buttons: Conditioned on Authentication */}
        <div className="nav-actions">
          {currentUser ? (
            /* Logged in state */
            <div className="nav-auth-user-group">
              <button className="btn btn-gold gotodashboard-btn" onClick={onGoToDashboard}>
                <span>Go to Dashboard</span>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
              <div className="user-nav-badge">
                <span className="user-nav-avatar">👤</span>
                <span className="user-nav-name">{currentUser.email.split('@')[0]}</span>
                <span className="user-nav-role">{currentUser.role.toUpperCase()}</span>
              </div>
              <button className="btn btn-outline logout-nav-btn" onClick={onLogout} title="Logout">
                Logout
              </button>
            </div>
          ) : (
            /* Not logged in state */
            <>
              <button className="btn btn-outline signin-btn" onClick={onSignInClick}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Sign In
              </button>
              <button className="btn btn-gold getstarted-btn" onClick={onRegisterClick}>
                Get Started
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
