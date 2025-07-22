"""
Run the object detection app specifically with webcam.
This script tries different camera indices to find an available camera.
"""
import cv2
from main import ObjectDetectionApp
from camera import OpenCVCamera
from detection import ContourDetector
from color import HSVColorAnalyzer
from config import ConfigManager


def find_available_camera():
    """Find an available camera by trying different indices."""
    print("🔍 Searching for available cameras...")
    
    for camera_index in range(5):  # Try camera indices 0-4
        print(f"  Trying camera index {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Found working camera at index {camera_index}")
                cap.release()
                return camera_index
        cap.release()
    
    print("❌ No working camera found")
    return None


def main():
    """Main function to run the object detection app with webcam."""
    print("🎯 Object Detection with Webcam")
    print("=" * 50)
    
    # Find available camera
    camera_index = find_available_camera()
    
    if camera_index is None:
        print("\n⚠️  No camera detected!")
        print("Options:")
        print("1. Connect a webcam and try again")
        print("2. Run 'python demo.py' to see the system work with test images")
        return
    
    print(f"\n🎬 Starting object detection with camera {camera_index}")
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press ESC to quit")
    
    # Create custom camera with the found index
    camera = OpenCVCamera(camera_index=camera_index, width=640, height=480)
    
    # Create app with custom camera
    app = ObjectDetectionApp(camera=camera)
    
    # Run the app
    app.run()


if __name__ == "__main__":
    main()
