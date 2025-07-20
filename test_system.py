"""
Test script for the object detection system.
This script provides basic testing functionality to verify components work correctly.
"""
import numpy as np
import cv2
from camera import OpenCVCamera
from detection import ContourDetector
from color import HSVColorAnalyzer
from models import BoundingBox, DetectedObject
from config import ConfigManager


def test_camera():
    """Test camera functionality."""
    print("Testing camera...")
    camera = OpenCVCamera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return False
    
    print("✅ Camera initialized successfully")
    
    frame = camera.capture_frame()
    if frame is None:
        print("❌ Frame capture failed")
        camera.release()
        return False
    
    print(f"✅ Frame captured successfully: {frame.shape}")
    
    resolution = camera.get_resolution()
    print(f"✅ Camera resolution: {resolution}")
    
    camera.release()
    return True


def test_detector():
    """Test object detector."""
    print("\nTesting object detector...")
    detector = ContourDetector()
    
    # Create a test image with simple shapes
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add some shapes
    cv2.rectangle(test_image, (50, 50), (150, 150), (255, 255, 255), -1)
    cv2.circle(test_image, (300, 200), 50, (255, 255, 255), -1)
    cv2.rectangle(test_image, (450, 100), (550, 200), (255, 255, 255), -1)
    
    objects = detector.detect_objects(test_image)
    print(f"✅ Detected {len(objects)} objects")
    
    for i, obj in enumerate(objects):
        print(f"  Object {i+1}: Area={obj.area}, Confidence={obj.confidence:.2f}")
    
    return len(objects) > 0


def test_color_analyzer():
    """Test color analyzer."""
    print("\nTesting color analyzer...")
    analyzer = HSVColorAnalyzer()
    
    # Create test images with different colors
    test_colors = [
        ((255, 0, 0), "red"),
        ((0, 255, 0), "green"),
        ((0, 0, 255), "blue"),
        ((255, 255, 0), "yellow")
    ]
    
    for (r, g, b), expected_color in test_colors:
        # Create test image
        test_image = np.full((100, 100, 3), (b, g, r), dtype=np.uint8)  # BGR for OpenCV
        
        # Create mock detected object
        bbox = BoundingBox(10, 10, 80, 80)
        contour = np.array([[10, 10], [90, 10], [90, 90], [10, 90]])
        detected_object = DetectedObject(bbox, contour)
        
        # Analyze color
        color = analyzer.analyze_color(test_image, detected_object)
        print(f"  Expected: {expected_color}, Detected: {color.name} (confidence: {color.confidence:.2f})")
    
    supported_colors = analyzer.get_supported_colors()
    print(f"✅ Color analyzer supports {len(supported_colors)} colors: {supported_colors}")
    
    return True


def test_config_manager():
    """Test configuration manager."""
    print("\nTesting configuration manager...")
    config_manager = ConfigManager()
    
    try:
        detection_config = config_manager.get_detection_config()
        print("✅ Detection config loaded successfully")
        
        color_config = config_manager.get_color_config()
        print("✅ Color config loaded successfully")
        
        # Test specific config access
        camera_width = config_manager.get_config("detection_config", "camera.width")
        print(f"✅ Camera width from config: {camera_width}")
        
        return True
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        return False


def run_visual_test():
    """Run a visual test with live camera feed."""
    print("\nRunning visual test (press 'q' to quit)...")
    
    camera = OpenCVCamera()
    detector = ContourDetector()
    color_analyzer = HSVColorAnalyzer()
    
    if not camera.initialize():
        print("❌ Cannot initialize camera for visual test")
        return
    
    cv2.namedWindow("Visual Test", cv2.WINDOW_AUTOSIZE)
    
    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                continue
            
            # Detect objects
            objects = detector.detect_objects(frame)
            
            # Analyze colors and visualize
            for obj in objects:
                obj.color = color_analyzer.analyze_color(frame, obj)
                
                # Draw bounding box
                bbox = obj.bounding_box
                cv2.rectangle(frame, (bbox.x, bbox.y), 
                            (bbox.x + bbox.width, bbox.y + bbox.height),
                            (0, 255, 0), 2)
                
                # Draw color label
                if obj.color:
                    label = f"{obj.color.name} ({obj.color.confidence:.2f})"
                    cv2.putText(frame, label, (bbox.x, bbox.y - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show object count
            cv2.putText(frame, f"Objects: {len(objects)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow("Visual Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Visual test interrupted")
    finally:
        camera.release()
        cv2.destroyAllWindows()


def main():
    """Run all tests."""
    print("🧪 Object Detection System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Camera", test_camera),
        ("Object Detector", test_detector),
        ("Color Analyzer", test_color_analyzer),
        ("Configuration Manager", test_config_manager)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready to use.")
        
        # Ask user if they want to run visual test
        response = input("\nWould you like to run the visual test? (y/n): ")
        if response.lower() in ['y', 'yes']:
            run_visual_test()
    else:
        print("⚠️  Some tests failed. Please check the system configuration.")


if __name__ == "__main__":
    main()
