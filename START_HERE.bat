@echo off
REM START_HERE.bat - One-command project startup (Windows)

echo.
echo 🚀 Football Predictor - One-Command Startup
echo ===========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Install from https://www.python.org/
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Install from https://nodejs.org/
    exit /b 1
)

echo ✅ Python: 
python --version

echo ✅ Node.js:
node --version

echo.
echo 📦 Setting up backend...
cd backend

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul

echo 🟢 Starting backend on http://localhost:8000
start "Backend" python -m uvicorn app.main:app --reload

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo 📦 Setting up frontend...
cd ..\frontend

if not exist "node_modules" (
    call npm install -q
)

echo 🟢 Starting frontend on http://localhost:5173
start "Frontend" npm run dev

echo.
echo ✅ Project started!
echo ===========================================
echo 📱 Frontend: http://localhost:5173
echo 🔌 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in terminal windows to stop servers
echo.

REM Open browser (optional)
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

pause
