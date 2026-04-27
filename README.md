# DHMB - Digital Handicraft Marketplace for Balochistan

A progressive web app (PWA) and analytics-backed marketplace prototype that helps artisans in Balochistan showcase products, understand demand trends, and connect with buyers.

## Project Overview

This project combines:
- **Marketplace flows** for artisans, buyers, and admin users
- **Big data analysis outputs** from CSV pipelines
- **Pricing and demand insights** surfaced through APIs
- **PWA support** (manifest + service worker + offline page)

The backend is built with Flask and serves both the API and the frontend.

## Tech Stack

- Python
- Flask
- Flask-CORS
- Pandas
- HTML/CSS/JavaScript
- Chart.js
- Service Worker + Web App Manifest (PWA)

## Repository Structure

- `app.py` - compatibility launcher so `python app.py` still works
- `backend/app.py` - main Flask app, API routes, auth/session logic, static file serving
- `frontend/` - `index.html`, `offline.html`, `service-worker.js`, `manifest.webmanifest`, `icon.svg`
- `data/processed/` - analytics CSV datasets used by APIs
- `data/runtime/` - local runtime storage (`users.json`, `listings.json`, `messages.json`, `orders.json`)
- `scripts/` - scraper, simulation, optimization, and helper scripts
- `docs/` - generated or supporting documents

## Getting Started

### 1) Clone the project

```bash
git clone <your-repo-url>
cd BDA-PROJECT
```

### 2) Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install flask flask-cors pandas
```

### 4) Run the app

```bash
python app.py
```

Then open:
- `http://localhost:5000`
- Health check: `http://localhost:5000/api/health`

## Environment Variables

- `DHMB_SECRET_KEY` - session secret key for Flask
- `FLASK_DEBUG` - set to `1` for debug mode

Example (PowerShell):

```powershell
$env:DHMB_SECRET_KEY="replace-with-a-secure-secret"
$env:FLASK_DEBUG="1"
python app.py
```

## Demo Accounts (Seeded on First Run)

If runtime JSON files do not exist, the app seeds default users:
- Artisan: `zainab@dhmb.local` / `artisan123`
- Artisan: `samia@dhmb.local` / `artisan123`
- Admin: `admin@dhmb.local` / `admin123`
- Buyer: `buyer@dhmb.local` / `buyer123`

## Main API Areas

- Auth: `/api/signup`, `/api/login`, `/api/logout`, `/api/me`
- Analytics: `/api/pipeline`, `/api/kpis`, `/api/demand`, `/api/districts`
- Pricing/Segmentation: `/api/price-optimization`, `/api/segments`, `/api/buyers`, `/api/top-products`
- Marketplace: `/api/catalog`, `/api/listings`, `/api/messages`, `/api/orders`

## PWA Features

- Installable app manifest
- Service worker caching for app shell and API fallback
- Offline fallback page
- Multi-route support (`/`, `/admin`, `/artisan`, `/buyer`)

## Suggested Next Improvements

- Add a `requirements.txt` and lock dependencies
- Add automated tests for core API routes
- Move JSON storage to a database (PostgreSQL/MySQL) for production
- Add CI checks (lint, test, security scanning)
- Deploy with Gunicorn + reverse proxy (Nginx) for production readiness

## License

Add your preferred license (for example, MIT) in a `LICENSE` file.
