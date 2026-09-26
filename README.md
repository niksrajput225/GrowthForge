# ⚡ GrowthForge - Production Habit & Skill Tracker

[![Tests](https://img.shields.io/badge/pytest-15%20passed-brightgreen.svg)]()
[![Android SDK](https://img.shields.io/badge/Android%20Target%20SDK-34%20%7C%2035-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

**GrowthForge** is an enterprise-grade personal growth, habit tracking, and skill progression application built with Python Flask, PostgreSQL/SQLite, PWA service workers, and Capacitor for Android native packaging ready for publishing on the **Google Play Store**.

---

## 📱 Features

- **Daily Quests & Prioritization**: High, medium, and low priority daily task management with celebratory confetti upon 100% daily completion.
- **Dynamic Skill Trees**: Hierarchical discipline tracking (categories -> modules -> metric logs) with custom color themes (Cyan, Gold, Emerald, Violet).
- **Gamified XP & Streaks**: Earn +15 XP per daily task, +30 XP per weekly goal, and +10 XP per skill log. Live level progression and streak flame counters.
- **Dual Authentication Engine**:
  - **JWT Bearer Tokens** (`/api/v1/auth/*`) for mobile Android/Capacitor WebView clients.
  - **Secure Session Cookies** with CSRF protection for desktop web browsers.
- **Offline-First Resilience**: Service Worker (`sw.js`) and client-side caching ensure the app never crashes or displays web errors when internet connection drops.
- **Google Play Store Compliance**: Built-in in-app and web account deletion (`/account/delete`) and GDPR/Google Play compliant Privacy Policy (`/privacy-policy`).
- **Cloud CI/CD Pipeline**: GitHub Actions workflow that builds signed/unsigned `.aab` (Android App Bundle) and `.apk` files directly in the cloud.

---

## 🛠️ Project Structure

```
growthforge-app/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── config.py                # Environment configs (Dev, Test, Prod)
│   ├── extensions.py            # db, migrate, login_manager, limiter, cors, JWT
│   ├── models/                  # User, Task, WeeklyTask, Skill, Note
│   ├── api/                     # RESTful API v1 (JWT-authenticated)
│   ├── web/                     # Web views & compliance legal pages
│   ├── static/
│   │   ├── css/app.css          # OLED dark theme & mobile layout
│   │   ├── js/app.js            # Frontend REST client & gamification engine
│   │   ├── js/sw.js             # PWA Service Worker for offline resilience
│   │   ├── icons/               # 192, 512, maskable icons & SVG
│   │   └── manifest.json        # Web App Manifest
│   └── templates/               # Jinja2 mobile templates
├── android/                     # Android native project targeting SDK 34
├── store_assets/                # 512x512 icon & 1024x500 Feature Graphic
├── .github/workflows/           # Automated Android .aab cloud build
├── tests/                       # 15 automated pytest tests
├── capacitor.config.json        # Capacitor native wrapper config
├── package.json                 # Node dependencies
├── Dockerfile                   # Multi-stage production container
├── docker-compose.yml           # App + PostgreSQL + Redis
├── gunicorn.conf.py             # Production WSGI server
├── PLAYSTORE_GUIDE.md           # Step-by-step Play Store handbook
└── run.py                       # Application entry point
```

---

## 🚀 Quickstart (Local Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
npm install
```

### 2. Generate Store Graphics & Icons
```bash
python scripts/generate_icons.py
```

### 3. Run Development Server
```bash
python run.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```bash
python -m pytest tests/ -v
```

---

## 🐳 Running with Docker

Spin up the entire production stack (Flask + PostgreSQL + Redis):
```bash
docker-compose up --build
```

---

## 📲 Building for Google Play Store

See the dedicated [PLAYSTORE_GUIDE.md](file:///C:/Users/Nisha%20kumari/.gemini/antigravity/scratch/growthforge-app/PLAYSTORE_GUIDE.md) for full instructions:
- **Cloud Build**: Push to GitHub and download the compiled `.aab` file from the **Actions** tab.
- **Local Build**: Run `npx cap sync && npx cap open android` with Android Studio.
