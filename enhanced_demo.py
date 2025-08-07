"""
Enhanced demo script for the improved object detection system.
This demo showcases the enhanced color and shape detection capabilities.
"""
import cv2
import numpy as np
import time
from main import ObjectDetectionApp
from camera import OpenCVCamera
from detection import ContourDetector
from color import HSVColorAnalyzer
from shape import GeometricShapeAnalyzer


def create_test_objects():
    """Create a test image with various colored shapes."""
    # Create a white background
    image = np.full((600, 800, 3), (255, 255, 255), dtype=np.uint8)
    
    # Red circle
    cv2.circle(image, (150, 150), 60, (0, 0, 255), -1)
    
    # Green square
    cv2.rectangle(image, (250, 90), (350, 190), (0, 255, 0), -1)
    
    # Blue triangle
    triangle_pts = np.array([[450, 90], [400, 190], [500, 190]], np.int32)
    cv2.fillPoly(image, [triangle_pts], (255, 0, 0))
    
    # Yellow rectangle
    cv2.rectangle(image, (580, 90), (680, 160), (0, 255, 255), -1)
    
    # Orange hexagon (approximated)
    hexagon_pts = np.array([
        [150, 300], [120, 340], [120, 380], [150, 420], [180, 380], [180, 340]
    ], np.int32)
    cv2.fillPoly(image, [hexagon_pts], (0, 165, 255))
    
    # Purple pentagon (approximated)
    pentagon_pts = np.array([
        [350, 300], [320, 330], [330, 370], [370, 370], [380, 330]
    ], np.int32)
    cv2.fillPoly(image, [pentagon_pts], (128, 0, 128))
    
    # Cyan ellipse (will be detected as circle)
    cv2.ellipse(image, (550, 350), (50, 30), 0, 0, 360, (255, 255, 0), -1)
    
    # Pink irregular shape
    irregular_pts = np.array([
        [100, 480], [140, 460], [180, 480], [170, 520], [130, 540], [90, 520]
    ], np.int32)
    cv2.fillPoly(image, [irregular_pts], (203, 192, 255))
    
    return image


def demo_with_test_image():
    """Demo using a test image with known shapes and colors."""
    print("🎨 Enhanced Object Detection Demo - Test Image")
    print("=" * 60)
    
    # Create test image
    test_image = create_test_objects()
    
    # Initialize components
    detector = ContourDetector(min_contour_area=1000, max_contour_area=50000)
    color_analyzer = HSVColorAnalyzer()
    shape_analyzer = GeometricShapeAnalyzer()
    
    # Detect objects
    detected_objects = detector.detect_objects(test_image)
    
    print(f"📍 Detected {len(detected_objects)} objects")
    print("-" * 40)
    
    # Analyze each object
    for i, obj in enumerate(detected_objects):
        obj.color = color_analyzer.analyze_color(test_image, obj)
        obj.shape = shape_analyzer.analyze_shape(obj)
        
        print(f"Object {i+1}:")
        print(f"  🎨 Color: {obj.color.name} (confidence: {obj.color.confidence:.2f})")
        print(f"  📐 Shape: {obj.shape.name} (confidence: {obj.shape.confidence:.2f})")
        print(f"  📏 Area: {obj.area} pixels")
        print(f"  📐 Vertices: {obj.shape.vertices}")
        print(f"  📊 Area Ratio: {obj.shape.area_ratio:.2f}")
        print(f"  📏 Aspect Ratio: {obj.shape.aspect_ratio:.2f}")
        print()
    
    # Visualize results
    result_image = test_image.copy()
    font_scale = 0.6
    thickness = 2
    
    for i, obj in enumerate(detected_objects):
        # Draw bounding box
        bbox = obj.bounding_box
        cv2.rectangle(result_image, 
                     (bbox.x, bbox.y), 
                     (bbox.x + bbox.width, bbox.y + bbox.height),
                     (255, 0, 0), thickness)
        
        # Draw contour
        cv2.drawContours(result_image, [obj.contour], -1, (0, 255, 0), thickness)
        
        # Draw labels
        color_label = f"{obj.color.name} ({obj.color.confidence:.2f})"
        shape_label = f"{obj.shape.name} ({obj.shape.confidence:.2f})"
        
        # Color label
        cv2.putText(result_image, color_label, 
                   (bbox.x, bbox.y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        
        # Shape label
        cv2.putText(result_image, shape_label, 
                   (bbox.x, bbox.y - 35),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    
    # Display results
    try:
        cv2.imshow("Original Test Image", test_image)
        cv2.imshow("Detection Results", result_image)
        print("🖼️  Images displayed. Press any key to continue...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except cv2.error:
        print("⚠️  GUI display not available, but detection analysis completed successfully!")


def demo_with_camera():
    """Demo using live camera feed."""
    print("\n🎥 Enhanced Object Detection Demo - Live Camera")
    print("=" * 60)
    print("Starting enhanced object detection with live camera...")
    print("📋 Features:")
    print("  • Real-time color detection with improved accuracy")
    print("  • Shape classification (circle, square, triangle, etc.)")
    print("  • Enhanced preprocessing for better detection")
    print("  • Confidence scores for both color and shape")
    print("\n🎮 Controls:")
    print("  • Press 'q' to quit")
    print("  • Press 'c' to capture and analyze current frame")
    print("  • Press 's' to save current frame")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    app = ObjectDetectionApp()
    app.run()


def main():
    """Main demo function."""
    print("🚀 Enhanced Object Detection System Demo")
    print("=" * 60)
    print("This demo showcases the improved object detection capabilities:")
    print("  ✨ Enhanced color detection with better accuracy")
    print("  🔺 Shape detection and classification")
    print("  🎯 Improved confidence scoring")
    print("  🛠️  Better image preprocessing")
    print()
    
    # Ask user which demo to run
    print("Select demo mode:")
    print("1. Test with predefined shapes (recommended)")
    print("2. Live camera demo")
    print("3. Both demos")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        demo_with_test_image()
    elif choice == "2":
        demo_with_camera()
    elif choice == "3":
        demo_with_test_image()
        input("\nPress Enter to continue to camera demo...")
        demo_with_camera()
    else:
        print("Invalid choice. Running test image demo...")
        demo_with_test_image()
    
    print("\n🎉 Demo completed! Thank you for trying the enhanced object detection system.")


if __name__ == "__main__":
    main()
