# FraudShield AI — Frontend (TypeScript + React)

A high-tech, responsive frontend for **FraudShield AI** ("*Secure Today. Safer Tomorrow.*"), designed to match the provided design mockup with dark-mode cyber aesthetics, glowing gold neon accents, and crimson alert gradients.

---

## 🌟 Features & Design Specifications

1. **Top Showcase / Hero Landing Page**:
   - **Header**: High-res SVG shield logo with glowing fingerprint, navigation links (*Home, Features, Solutions, Technology, Use Cases, About, Contact*), *Sign In* modal, and *Get Started* CTA.
   - **Hero Section**:
     - `⚡ AI-Powered Financial Security` glowing pill badge.
     - Headline: **FraudShield AI — Smart Fraud Detection. Safer Transactions.**
     - Action buttons: `Explore Platform →` and `▶ Watch Demo`.
     - 4 Key Value Metric Badges:
       - 🛡️ **99.7%** Detection Accuracy
       - ⚡ **Real-Time** Monitoring
       - 📊 **AI-Powered** Analytics
       - 🔒 **Enterprise** Grade Security
     - 3D Holographic Visual Composition:
       - Floating **Credit Card** & **Debit Card** (`5321 7700 0000 1234`, EMV chip, contactless waves).
       - Tiered glowing golden pedestal with holographic shield hologram.
       - Hooded cyber hacker silhouette with glowing red eyes and floating **Fraud Risk: 98.5% High Risk** widget.

2. **Operations & Admin Dashboard**:
   - **Left Sidebar**: Active glowing gold tab indicator, navigation items (*Dashboard, Fraud Detection, Transactions, Analytics, Reports, Alerts (badge '3'), Users, Settings, Logout*).
   - **Topbar**: Search bar, Real-time Live Stream toggle, notification bell with badge, Admin user profile.
   - **Dashboard Overview**:
     - 4 Primary Metric Cards:
       - 💳 **Total Transactions**: 12,480 (+12.5% with gold sparkline chart).
       - 🛡️ **Fraud Detected**: 128 (+8.3% with red glow alert card and sparkline).
       - ⏱️ **Risk Rate**: 1.03% (-0.21% favorable reduction).
       - 👥 **Active Users**: 2,540 (+15.7%).
     - **Fraud Trends**: Interactive dual-line chart (Mon–Sun) comparing Legitimate vs Fraudulent volume.
     - **Detection by Model**: Donut chart with 96.7% Accuracy in center (XGBoost 34%, Random Forest 32%, Isolation Forest 34%).
     - **Recent Alerts Feed**: Priority alerts with timestamps and quick-action resolution.
     - **Promo Card**: "Stay Protected with FraudShield AI" + `Upgrade Plan →`.

3. **Interactive Subsystems**:
   - **🎯 Fraud Prediction Sandbox**: Form connected to `POST /api/v1/predictions` with test presets (*Normal E-Commerce, Suspicious Travel, Critical Syndicate*), risk score meter (0–100), risk tier badge (LOW/MEDIUM/HIGH), and explanation bullet points.
   - **💳 Transactions Ledger**: Live searchable table of all transactions with risk metrics.
   - **🔔 Alerts Center**: Real-time modal to investigate and update alert statuses (`open`, `in_review`, `resolved`, `dismissed`) via `PATCH /api/v1/alerts/{id}`.
   - **⚙️ Backend Connectivity Settings**: Real-time `/health/live` probe, latency monitor, and seamless fallback between Live FastAPI Backend and High-Fidelity Standalone Demo Mode.

---

## 🛠️ Technology Stack

- **Language**: TypeScript (`.ts`, `.tsx`) with strict mode enabled
- **UI Framework**: React 18 + React DOM
- **Build System**: Vite 5
- **Styling**: Cyberpunk Dark Gold & Crimson CSS3 with glassmorphism, glowing SVG filters, and KaTeX / Flexbox / CSS Grid
- **Backend Integration**: FastAPI REST client (`frontend/src/services/api.ts`)

---

## 🚀 How to Run

### Option 1: Vite Development Server (Recommended for development)
```powershell
cd frontend
npm run dev
```
Opens on **http://localhost:5500**. Any changes to TypeScript code hot-reload automatically.

### Option 2: Served Directly by FastAPI Backend
The FastAPI backend (`app/main.py`) has been configured to serve the `frontend/` directory directly at `/`:
```powershell
# From project root:
uvicorn app.main:app --reload
```
Open **http://localhost:8000** in your browser. Both the web interface and the REST API (`/api/v1/...`) run together on the same port with zero CORS configuration needed!

### Option 3: Standalone Python Server
```powershell
python frontend/server.py
```
Or:
```powershell
python -m http.server 5500 --directory frontend
```
Opens on **http://localhost:5500**.

### Option 4: Production Build
```powershell
cd frontend
npm run build
```
Creates optimized production assets in `frontend/dist/`.

---

## 📁 File Structure

```text
frontend/
├── package.json                   # Dependencies, TypeScript and Vite scripts
├── tsconfig.json                  # TypeScript compiler options
├── vite.config.ts                 # Vite bundler & API reverse proxy config
├── index.html                     # Main application entry point
├── server.py                      # Lightweight development HTTP server
├── assets/
│   ├── shield-fingerprint.svg     # Official FraudShield AI logo with glowing fingerprint
│   ├── cards.svg                  # Floating Credit & Debit cards illustration
│   ├── hacker-graphic.svg         # Hooded adversary silhouette with risk monitor
│   └── pedestal-shield.svg        # Tiered gold pedestal stage
├── css/
│   ├── main.css                   # Global variables, glassmorphic panels, buttons, modals, toasts
│   ├── landing.css                # Landing page header, hero layout, 3D card animations
│   └── dashboard.css              # Sidebar, stats cards, trends chart, donut chart, alerts feed
├── js/
│   └── standalone-bundle.js       # Immediate browser execution engine
└── src/
    ├── main.tsx                   # React entry point
    ├── App.tsx                    # Main state orchestrator & view switcher
    ├── types/
    │   └── api.ts                 # Full TypeScript definitions matching app/schemas.py
    ├── services/
    │   └── api.ts                 # REST client connected to FastAPI / fallback engine
    └── components/
        ├── Header.tsx             # Landing navigation bar
        ├── Hero.tsx               # Landing hero with 3D cards & hacker monitor
        ├── Sidebar.tsx            # Dashboard sidebar with active gold tab
        ├── DashboardOverview.tsx  # Metrics cards, trends chart, donut chart, alerts
        ├── FraudDetectionSandbox.tsx # Interactive test form for /api/v1/predictions
        ├── TransactionsTable.tsx  # Transactions ledger
        ├── AlertsManager.tsx      # Alerts investigation and status updater
        ├── LoginModal.tsx         # JWT Authentication modal
        └── BackendSettingsModal.tsx # Backend connectivity & health tester
```

---

## 🔗 Backend API Endpoints Integrated

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health/live` | Live connection health probe |
| `POST` | `/api/v1/auth/login` | JWT access token authentication |
| `GET` | `/api/v1/auth/me` | Fetch active user credentials & role |
| `GET` | `/api/v1/dashboard/summary` | Summary counts of transactions & flagged events |
| `GET` | `/api/v1/analytics/trends` | 7-day rolling transaction & flag counts |
| `POST` | `/api/v1/predictions` | Real-time AI fraud risk index scoring |
| `GET` | `/api/v1/transactions` | Paginated transactions ledger |
| `GET` | `/api/v1/alerts` | Active priority fraud alerts queue |
| `PATCH` | `/api/v1/alerts/{id}` | Update alert status (`in_review`, `resolved`, `dismissed`) |
| `GET` | `/api/v1/models/active` | Active ML model metadata and version |
