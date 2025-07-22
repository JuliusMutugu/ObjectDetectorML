@echo off
REM Object Detector Mobile App Launcher (Windows)
REM This script helps start both the Python backend and Flutter app

echo 🚀 Object Detector Mobile App Launcher
echo =======================================

REM Check if we're in the right directory
if not exist "python_backend" (
    echo ❌ Error: Please run this script from the mobile_app directory
    echo    Expected structure:
    echo    mobile_app/
    echo    ├── python_backend/
    echo    └── flutter_app/
    pause
    exit /b 1
)

if not exist "flutter_app" (
    echo ❌ Error: Please run this script from the mobile_app directory
    echo    Expected structure:
    echo    mobile_app/
    echo    ├── python_backend/
    echo    └── flutter_app/
    pause
    exit /b 1
)

echo 🐍 Starting Python Backend...
cd python_backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Start the API server in background
echo 🌐 Starting FastAPI server on http://127.0.0.1:8000
start "Backend Server" cmd /k "uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

cd ..

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Test backend connection
echo 🔄 Testing backend connection...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Backend is responding
) else (
    echo    ⚠️  Backend may still be starting up
)

echo.
echo 📱 Starting Flutter App...
cd flutter_app

REM Get Flutter dependencies
echo 📥 Getting Flutter dependencies...
flutter pub get

REM Check for connected devices
echo 📱 Checking for connected devices...
flutter devices

echo.
echo 🎯 Ready to start Flutter app!
echo    Backend: http://127.0.0.1:8000
echo    Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to start the Flutter app...
pause >nul

REM Start the Flutter app
echo 🚀 Starting Flutter app...
flutter run

cd ..

echo.
echo 👋 Flutter app finished. Backend server is still running in separate window.
echo    Close the backend server window manually when done.
pause
