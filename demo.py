"""
Demo script for the object detection system without requiring a camera.
This creates synthetic test images to demonstrate the functionality.
"""
import cv2
import numpy as np
import time
from detection import ContourDetector
from color import HSVColorAnalyzer
from models import DetectionResult
from config import ConfigManager
from utils import VisualizationUtils


def create_test_image_with_colored_objects():
    """Create a test image with colored objects."""
    # Create a white background
    img = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Add colored rectangles with black borders
    cv2.rectangle(img, (50, 50), (150, 150), (0, 0, 255), -1)      # Red rectangle
    cv2.rectangle(img, (50, 50), (150, 150), (0, 0, 0), 2)        # Black border
    
    cv2.rectangle(img, (200, 50), (300, 150), (0, 255, 0), -1)    # Green rectangle
    cv2.rectangle(img, (200, 50), (300, 150), (0, 0, 0), 2)       # Black border
    
    cv2.rectangle(img, (350, 50), (450, 150), (255, 0, 0), -1)    # Blue rectangle
    cv2.rectangle(img, (350, 50), (450, 150), (0, 0, 0), 2)       # Black border
    
    # Add colored circles with black borders
    cv2.circle(img, (100, 300), 50, (0, 255, 255), -1)            # Yellow circle
    cv2.circle(img, (100, 300), 50, (0, 0, 0), 2)                 # Black border
    
    cv2.circle(img, (300, 300), 50, (255, 255, 0), -1)            # Cyan circle
    cv2.circle(img, (300, 300), 50, (0, 0, 0), 2)                 # Black border
    
    cv2.circle(img, (500, 300), 50, (128, 0, 128), -1)            # Purple circle
    cv2.circle(img, (500, 300), 50, (0, 0, 0), 2)                 # Black border
    
    return img


def run_demo():
    """Run the object detection demo."""
    print("🎯 Object Detection System Demo")
    print("=" * 50)
    
    # Initialize components
    config_manager = ConfigManager()
    detector = ContourDetector()
    color_analyzer = HSVColorAnalyzer()
    
    # Configure detector for better results with test images
    detector.set_parameters(
        min_contour_area=500,
        max_contour_area=100000,
        blur_kernel_size=3,
        morph_kernel_size=3
    )
    
    # Create test image
    print("📷 Creating test image with colored objects...")
    test_image = create_test_image_with_colored_objects()
    
    # Detect objects
    print("🔍 Detecting objects...")
    detected_objects = detector.detect_objects(test_image)
    print(f"✅ Found {len(detected_objects)} objects")
    
    # Analyze colors
    print("🎨 Analyzing colors...")
    for i, obj in enumerate(detected_objects):
        obj.color = color_analyzer.analyze_color(test_image, obj)
        obj.object_id = i + 1
        print(f"  Object {obj.object_id}: {obj.color.name} (confidence: {obj.color.confidence:.2f}, area: {obj.area})")
    
    # Create detection result
    detection_result = DetectionResult(
        objects=detected_objects,
        frame=test_image,
        timestamp=time.time()
    )
    
    # Visualize results
    print("🖼️  Creating visualization...")
    display_frame = visualize_detection_results(detection_result)
    
    # Show the result
    cv2.namedWindow("Object Detection Demo", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("Object Detection Demo", display_frame)
    
    print("\n🎉 Demo complete!")
    print("📋 Summary:")
    print(f"   - Total objects detected: {len(detected_objects)}")
    print(f"   - Colors detected: {[obj.color.name for obj in detected_objects if obj.color]}")
    print("\nPress any key in the image window to close...")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def visualize_detection_results(detection_result: DetectionResult) -> np.ndarray:
    """Visualize detection results."""
    frame = detection_result.frame.copy()
    
    for obj in detection_result.objects:
        # Draw bounding box
        bbox = obj.bounding_box
        cv2.rectangle(frame, 
                     (bbox.x, bbox.y), 
                     (bbox.x + bbox.width, bbox.y + bbox.height),
                     (255, 255, 255), 2)
        
        # Draw contours
        cv2.drawContours(frame, [obj.contour], -1, (0, 255, 0), 2)
        
        # Draw color label
        if obj.color:
            label = f"ID:{obj.object_id} {obj.color.name} ({obj.color.confidence:.2f})"
            label_pos = (bbox.x, bbox.y - 10)
            
            # Background for text
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame,
                         (label_pos[0], label_pos[1] - text_size[1] - 5),
                         (label_pos[0] + text_size[0], label_pos[1] + 5),
                         (0, 0, 0), -1)
            
            # Text
            cv2.putText(frame, label, label_pos,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Add title
    title = f"Object Detection Demo - {len(detection_result.objects)} objects detected"
    cv2.putText(frame, title, (10, 25),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    return frame


def main():
    """Main entry point for the demo."""
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
