# Object Detector Mobile App

A Flutter mobile application with advanced computer vision capabilities including object detection, face recognition, hand tracking, and gesture-based interaction.

## Features

- **Object Detection**: Real-time color-based object detection and classification
- **Face Detection**: Face recognition with landmark detection
- **Hand Tracking**: Real-time hand pose estimation with 21 landmarks per hand
- **Gesture Recognition**: Interactive gestures for touch-free app control
- **Multi-Mode Processing**: Switch between different detection modes
- **Real-time Performance**: Live camera feed with overlay visualizations

## Requirements

- Flutter 3.0+
- Dart 3.0+
- Android 6.0+ / iOS 12.0+
- Camera permission
- Internet connection (for backend API)

## Backend API

This app requires the Python FastAPI backend to be running. The backend provides:
- Object detection endpoints
- Face detection with MediaPipe
- Hand tracking and gesture recognition
- WebSocket support for real-time processing

### Starting the Backend

1. Navigate to the backend directory:
   ```bash
   cd ../python_backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server:
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Installation

1. **Install Flutter**: Follow the [Flutter installation guide](https://flutter.dev/docs/get-started/install)

2. **Clone and setup**:
   ```bash
   cd mobile_app/flutter_app
   flutter pub get
   ```

3. **Run the app**:
   ```bash
   flutter run
   ```

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── screens/
│   ├── home_screen.dart      # Main navigation screen
│   ├── camera_screen.dart    # Real-time camera processing
│   └── settings_screen.dart  # Configuration screen
├── services/
│   ├── vision_service.dart   # Computer vision API service
│   └── camera_service.dart   # Camera management
└── widgets/
    ├── detection_overlay.dart # Visual overlays for detections
    └── gesture_controls.dart  # Interactive gesture UI
```

## Usage

### Navigation
- **Home Screen**: Choose between different detection modes
- **Object Detection**: Detect and classify colored objects
- **Face Detection**: Real-time face recognition
- **Hand Tracking**: Track hand movements and poses
- **Interactive Mode**: Use gestures to control the app

### Camera Controls
- **Mode Switch**: Toggle between detection modes
- **Camera Flip**: Switch between front/back cameras
- **Play/Pause**: Start/stop processing
- **Performance Info**: View FPS and detection counts

### Gesture Interactions
When in Interactive Mode, use these gestures:
- **Point**: Activate "Play" button
- **Fist**: Activate "Pause" button  
- **Thumbs Up**: Activate "Like" button
- **Thumbs Down**: Activate "Dislike" button
- **Peace Sign**: Navigate screens
- **Open Palm**: Reset interactions

### Settings
Configure the app through the Settings screen:
- **API URL**: Backend server address
- **Detection Features**: Enable/disable specific detection types
- **Performance**: Adjust confidence thresholds and processing intervals
- **Camera**: Resolution and focus settings

## API Configuration

The app connects to a Python FastAPI backend by default at `http://127.0.0.1:8000`. 

For different environments:
- **Local Development**: `http://127.0.0.1:8000`
- **Network Device**: `http://[YOUR_IP]:8000`
- **Production**: Update to your deployed backend URL

## Performance Optimization

- **Lower Resolution**: Reduce camera resolution for better performance
- **Increase Interval**: Process frames less frequently
- **Single Mode**: Use specific detection modes instead of "All"
- **Confidence Threshold**: Increase to reduce false positives

## Troubleshooting

### Camera Issues
- Ensure camera permissions are granted
- Check that camera is not being used by another app
- Try switching between front/back cameras

### Backend Connection
- Verify backend server is running
- Check firewall settings
- Test connection in Settings screen
- Ensure correct IP address for network access

### Performance Issues
- Close other camera apps
- Reduce processing frequency in Settings
- Use single detection modes instead of "All"
- Ensure good lighting conditions

## Development

### Adding New Features
1. Create new detection endpoints in the Python backend
2. Update `VisionService` to call new endpoints  
3. Add UI components in appropriate screens
4. Update overlay painter for new visualizations

### Custom Gestures
1. Train gesture recognition model in backend
2. Add gesture types to `VisionService`
3. Update `GestureControls` widget for new interactions
4. Map gestures to app functionality

## Dependencies

Key packages used:
- `camera`: Camera access and control
- `provider`: State management
- `http`: API communication
- `flutter/material`: UI components

## License

This project is part of the ObjectDetector system. See the main project README for license information.
