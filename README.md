# IronCrate 🛡️ — Web App

**Flask + React/Vite** rebuild of IronCrate.  
Tamper-proof vehicular incident logging with SHA-256 hashing and Polygon blockchain anchoring.

---

## Stack

| Layer      | Tech                          |
|------------|-------------------------------|
| Frontend   | React 18 + Vite + CSS Modules |
| Backend    | Flask 3 + Flask-CORS          |
| Blockchain | Web3.py → Polygon Amoy        |
| Storage    | Firebase Realtime DB + Storage|
| Hashing    | SHA-256 (Python hashlib)      |

---

## Project Structure

```
IronCrate_web/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── contracts/
│   │   └── IronCrateRegistry.sol
│   ├── core/
│   │   ├── crypto.py           # SHA-256 + Web3 anchoring
│   │   └── firebase.py         # Firebase DB + Storage wrapper
│   └── routes/
│       ├── auth.py             # Register / Login / Me
│       ├── session.py          # Upload video + anchor hash
│       └── incidents.py        # List + detail incidents
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx             # Router
        ├── api.js              # Axios instance
        ├── index.css           # Global styles
        ├── hooks/
        │   └── useAuth.jsx     # Auth context
        ├── components/
        │   ├── Navbar.jsx
        │   └── Navbar.module.css
        └── pages/
            ├── Landing.jsx     # Login page
            ├── Register.jsx    # Vehicle registration
            ├── Dashboard.jsx   # Stats + recent incidents
            ├── Record.jsx      # Webcam capture + upload
            └── Incidents.jsx   # Full incident log
```

---

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Fill in your Firebase and Polygon keys in .env

python app.py
# Runs on http://localhost:5000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

Vite proxies `/api/*` → `http://localhost:5000` automatically.

---

## Environment Variables (backend/.env)

| Key                      | Description                        |
|--------------------------|------------------------------------|
| `FLASK_SECRET`           | Random secret for sessions         |
| `POLYGON_RPC_URL`        | Polygon Amoy RPC endpoint          |
| `PRIVATE_KEY`            | Wallet private key (no 0x prefix)  |
| `CONTRACT_ADDRESS`       | Deployed IronCrateRegistry address |
| `FIREBASE_API_KEY`       | Firebase project API key           |
| `FIREBASE_AUTH_DOMAIN`   | e.g. project.firebaseapp.com       |
| `FIREBASE_DB_URL`        | Realtime DB URL                    |
| `FIREBASE_STORAGE_BUCKET`| e.g. project.appspot.com           |

---

## Deploy Contract

```bash
# From backend/contracts/ using Hardhat or Remix IDE
# Then paste the deployed address into .env as CONTRACT_ADDRESS
```

---

## Features

- **Vehicle registration** with owner info stored in Firebase
- **Webcam recording** via browser MediaRecorder API
- **SHA-256 hashing** of video blob on the server
- **Firebase Storage** upload with public URL
- **Polygon Amoy** blockchain anchoring of hash
- **Incident log** with expandable detail and PolygonScan links
- **GPS coordinates** captured from browser geolocation

---

*MCA Technical Project — 2026*
