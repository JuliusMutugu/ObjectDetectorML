# Vision AI Mobile App

A cross-platform mobile application for advanced computer vision tasks including object detection, facial recognition, hand tracking, and gesture-based interactions.

## Features

### 🎯 Core Vision Capabilities
- **Object Color Detection** - Real-time detection and color identification of multiple objects
- **Facial Detection** - Face detection and recognition
- **Hand Tracking** - Real-time hand movement and gesture recognition
- **Interactive Gestures** - Touch-free interaction with screen elements using hand gestures

### 📱 Mobile Features
- **Cross-Platform** - Works on both Android and iOS
- **Real-time Processing** - Live camera feed processing
- **Interactive UI** - Touch and gesture-based interface
- **Offline Capable** - Core features work without internet
- **Configurable** - Adjustable detection parameters

## Architecture

```
mobile_app/
├── flutter_app/          # Flutter frontend
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/       # App screens
│   │   ├── widgets/       # Reusable widgets
│   │   ├── services/      # API and camera services
│   │   └── models/        # Data models
│   ├── android/           # Android-specific code
│   ├── ios/              # iOS-specific code
│   └── pubspec.yaml      # Dependencies
├── python_backend/        # Python CV backend
│   ├── api/              # FastAPI REST endpoints
│   ├── vision/           # Computer vision modules
│   │   ├── object_detection.py
│   │   ├── face_detection.py
│   │   ├── hand_tracking.py
│   │   └── gesture_recognition.py
│   ├── models/           # AI models and weights
│   └── requirements.txt
└── shared/               # Shared configurations
    └── config/           # Configuration files
```

## Technology Stack

### Frontend (Flutter)
- **Framework**: Flutter 3.x
- **Camera**: camera plugin
- **Image Processing**: image plugin
- **HTTP Client**: dio
- **State Management**: Provider/Riverpod
- **UI Components**: Material Design 3

### Backend (Python)
- **API Framework**: FastAPI
- **Computer Vision**: OpenCV, MediaPipe
- **Machine Learning**: TensorFlow Lite, ONNX
- **Image Processing**: PIL, NumPy
- **Real-time**: WebSocket support

### Computer Vision Models
- **Object Detection**: YOLOv8 or MobileNet SSD
- **Face Detection**: MediaPipe Face Detection
- **Hand Tracking**: MediaPipe Hands
- **Gesture Recognition**: Custom trained model

## Getting Started

### Prerequisites
- Flutter SDK 3.x
- Python 3.9+
- Android Studio / Xcode
- Physical device or emulator

### Installation

1. **Clone and setup Python backend**:
```bash
cd python_backend
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

2. **Setup Flutter app**:
```bash
cd flutter_app
flutter pub get
flutter run
```

## Features in Detail

### 1. Object Detection & Color Recognition
- Real-time detection of multiple objects
- Color identification with confidence scores
- Bounding box visualization
- Object tracking across frames

### 2. Facial Detection & Recognition
- Real-time face detection
- Face landmark detection
- Optional face recognition
- Emotion detection (future feature)

### 3. Hand Tracking & Gestures
- 21-point hand landmark detection
- Gesture recognition (swipe, pinch, point, etc.)
- Hand-to-screen coordinate mapping
- Custom gesture training

### 4. Interactive Elements
- Virtual objects that respond to hand gestures
- Gesture-controlled UI navigation
- Air-tap functionality
- Virtual buttons and controls

## Configuration

All detection parameters can be configured through:
- `shared/config/app_config.yaml` - Main app settings
- `shared/config/vision_config.yaml` - Vision model parameters
- Flutter app settings screen

## API Endpoints

### Object Detection
- `POST /api/detect/objects` - Detect objects in image
- `WS /api/stream/objects` - Real-time object detection

### Face Detection
- `POST /api/detect/faces` - Detect faces in image
- `WS /api/stream/faces` - Real-time face detection

### Hand Tracking
- `POST /api/detect/hands` - Detect hands and gestures
- `WS /api/stream/hands` - Real-time hand tracking

## Performance Optimization

- **Model Optimization**: TensorFlow Lite models for mobile
- **Frame Skipping**: Process every N frames for better performance
- **Resolution Scaling**: Adaptive resolution based on device capability
- **Background Processing**: Non-blocking CV operations

## Future Enhancements

- [ ] 3D Object Detection
- [ ] Augmented Reality (AR) Features
- [ ] Voice Command Integration
- [ ] Multi-user Hand Tracking
- [ ] Machine Learning Model Training Interface
- [ ] Cloud Sync for Custom Models

## License

MIT License - Feel free to use and modify for your projects!
