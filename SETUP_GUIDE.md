# 🚀 Week 1 Phase 1 Setup Instructions

This guide walks you through setting up your local development environment for the Football Predictor project.

## Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/)

## Step 1: Python Backend Setup (15-20 minutes)

### 1.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Verify Installation

```bash
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
```

## Step 2: Node.js Frontend Setup (10-15 minutes)

### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

### 2.2 Verify Installation

```bash
npm list react
```

## Step 3: PostgreSQL Database Setup (10-15 minutes)

### 3.1 Create Database

Using `psql` or PostgreSQL admin tool:

```sql
CREATE DATABASE football_predictor_db;
CREATE USER football_dev WITH PASSWORD 'dev_password';
ALTER ROLE football_dev SET client_encoding TO 'utf8';
ALTER ROLE football_dev SET default_transaction_isolation TO 'read committed';
ALTER ROLE football_dev SET default_transaction_deferrable TO on;
ALTER ROLE football_dev SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE football_predictor_db TO football_dev;
```

### 3.2 Verify Connection

```bash
psql -U football_dev -d football_predictor_db -c "SELECT version();"
```

## Step 4: Environment Configuration (5 minutes)

### 4.1 Create .env File

```bash
cp .env.example .env
```

### 4.2 Update Local Values

Edit `.env` with your local setup:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://football_dev:dev_password@localhost:5432/football_predictor_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-local-secret-key
JWT_SECRET_KEY=your-local-jwt-secret
```

## Step 5: Verify Backend Startup

### 5.1 Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 5.2 Test Health Endpoint

Open browser or run:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Football Predictor API",
  "version": "0.1.0",
  "environment": "development"
}
```

## Step 6: Verify Frontend Startup

### 6.1 Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
```

### 6.2 Visit Application

Open [http://localhost:5173](http://localhost:5173) in your browser.

You should see the Football Predictor placeholder page.

## Step 7: Verify Backend-Frontend Connection

### 7.1 Test API Integration

In the browser console (F12), run:

```javascript
fetch('http://localhost:8000/api/v1')
  .then(r => r.json())
  .then(d => console.log(d))
```

Expected response:
```json
{
  "message": "Football Predictor API v1",
  "endpoints": {
    "auth": "/api/v1/auth",
    "matches": "/api/v1/matches",
    "predictions": "/api/v1/predictions",
    "users": "/api/v1/users"
  }
}
```

## Troubleshooting

### Python Issues

**ImportError: No module named 'fastapi'**
- Solution: Ensure venv is activated, then re-run `pip install -r requirements.txt`

**Connection refused to PostgreSQL**
- Solution: Verify PostgreSQL is running and credentials in .env match database setup

### Node Issues

**npm ERR! ERESOLVE unable to resolve dependency tree**
- Solution: Run `npm install --legacy-peer-deps`

**Port 5173 already in use**
- Solution: Kill process or change port: `npm run dev -- --port 5174`

### Database Issues

**FATAL: database "football_predictor_db" does not exist**
- Solution: Run SQL commands in Step 3.1 to create database and user

## Next Steps

✅ **Phase 1 Complete!** You now have:
- ✅ FastAPI backend running on http://localhost:8000
- ✅ React frontend running on http://localhost:5173
- ✅ PostgreSQL database configured
- ✅ Environment properly configured

🚀 **Next: Week 1 Phase 2 - Database Schema & Models**

See [ROADMAP.md](../docs/ROADMAP.md) for Week 2 objectives.

## Common Commands

```bash
# Backend: Start dev server
cd backend
python -m uvicorn app.main:app --reload

# Frontend: Start dev server
cd frontend
npm run dev

# Backend: Run tests
pytest

# Frontend: Run lint
npm run lint

# Frontend: Format code
npm run format
```

## Support

Having issues? Check:
1. [backend/README.md](backend/README.md) - Backend-specific setup
2. [frontend/README.md](frontend/README.md) - Frontend-specific setup
3. [README.md](README.md) - Main project documentation

