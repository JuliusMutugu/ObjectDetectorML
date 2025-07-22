#!/bin/bash

# Object Detector Mobile App Launcher
# This script helps start both the Python backend and Flutter app

echo "🚀 Object Detector Mobile App Launcher"
echo "======================================="

# Check if we're in the right directory
if [ ! -d "python_backend" ] || [ ! -d "flutter_app" ]; then
    echo "❌ Error: Please run this script from the mobile_app directory"
    echo "   Expected structure:"
    echo "   mobile_app/"
    echo "   ├── python_backend/"
    echo "   └── flutter_app/"
    exit 1
fi

# Function to start backend
start_backend() {
    echo "🐍 Starting Python Backend..."
    cd python_backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install dependencies
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Start the API server
    echo "🌐 Starting FastAPI server on http://127.0.0.1:8000"
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    return $BACKEND_PID
}

# Function to start Flutter app
start_flutter() {
    echo "📱 Starting Flutter App..."
    cd flutter_app
    
    # Get Flutter dependencies
    echo "📥 Getting Flutter dependencies..."
    flutter pub get
    
    # Check for connected devices
    echo "📱 Checking for connected devices..."
    flutter devices
    
    # Start the Flutter app
    echo "🚀 Starting Flutter app..."
    flutter run
    
    cd ..
}

# Function to cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   ✅ Backend stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Main execution
echo "Starting services..."
echo ""

# Start backend in background
start_backend
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to initialize
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Test backend connection
echo "🔄 Testing backend connection..."
if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "   ✅ Backend is responding"
else
    echo "   ⚠️  Backend may still be starting up"
fi

echo ""
echo "🎯 Ready to start Flutter app!"
echo "   Backend: http://127.0.0.1:8000"
echo "   Docs: http://127.0.0.1:8000/docs"
echo ""

# Start Flutter app
start_flutter

# Keep script running
wait
