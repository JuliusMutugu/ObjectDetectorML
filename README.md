# Object Color Detector

A modular object detection system using OpenCV and Python that identifies objects in camera feed and determines their colors.

## Features

- Real-time object detection from camera feed
- Color identification for detected objects
- Multiple object detection capability
- Modular architecture following SOLID principles
- Easy to extend and maintain

## Architecture

The system follows SOLID principles with a modular design:

### Core Components

1. **Camera Interface** (`camera/`)
   - `camera_interface.py`: Abstract camera interface
   - `opencv_camera.py`: OpenCV camera implementation

2. **Object Detection** (`detection/`)
   - `detector_interface.py`: Abstract detector interface
   - `contour_detector.py`: Contour-based object detection
   - `object_tracker.py`: Object tracking and management

3. **Color Analysis** (`color/`)
   - `color_analyzer_interface.py`: Abstract color analyzer interface
   - `hsv_color_analyzer.py`: HSV-based color analysis
   - `color_classifier.py`: Color classification logic

4. **Image Processing** (`processing/`)
   - `image_processor.py`: Image preprocessing utilities
   - `filters.py`: Various image filters

5. **Main Application** (`main.py`)
   - Entry point that orchestrates all components

## Installation

```bash
# Install dependencies
poetry install

# Run the application
poetry run python main.py
```

## Usage

1. Run the application: `poetry run python main.py`
2. Point your camera at objects
3. The system will detect objects and display their colors
4. Press 'q' to quit

## Configuration

The system uses configuration files to adjust detection parameters:

- `config/detection_config.yaml`: Object detection parameters
- `config/color_config.yaml`: Color classification settings

## Extending the System

Thanks to the modular architecture, you can easily:

- Add new detection algorithms by implementing `DetectorInterface`
- Add new color analysis methods by implementing `ColorAnalyzerInterface`
- Add new camera sources by implementing `CameraInterface`
- Modify processing pipelines in the `processing` module

## SOLID Principles Implementation

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend with new implementations
- **Liskov Substitution**: Interfaces ensure substitutability
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depends on abstractions, not concretions
