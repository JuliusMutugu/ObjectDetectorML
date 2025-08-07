"""
Debug script to test the enhanced detection system.
"""
import cv2
import numpy as np
from detection import ContourDetector
from color import HSVColorAnalyzer
from shape import GeometricShapeAnalyzer


def create_simple_test():
    """Create a simple test image."""
    # Create a black background with white shapes
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Large white circle
    cv2.circle(image, (150, 200), 80, (255, 255, 255), -1)
    
    # Large white rectangle
    cv2.rectangle(image, (300, 120), (450, 280), (255, 255, 255), -1)
    
    return image


def debug_detection():
    """Debug the detection process."""
    print("🔍 Debugging Object Detection")
    print("=" * 40)
    
    # Create test image
    test_image = create_simple_test()
    
    # Save original image for inspection
    cv2.imwrite("debug_original.jpg", test_image)
    print("✅ Original image saved as debug_original.jpg")
    
    # Initialize detector with lower area threshold
    detector = ContourDetector(min_contour_area=100, max_contour_area=100000)
    
    # Debug the preprocessing step
    gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("debug_gray.jpg", gray)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite("debug_blurred.jpg", blurred)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imwrite("debug_edges.jpg", edges)
    
    # Find contours directly
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} raw contours")
    
    # Filter contours by area
    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        print(f"Contour area: {area}")
        if 100 <= area <= 100000:
            valid_contours.append(contour)
    
    print(f"Valid contours after filtering: {len(valid_contours)}")
    
    # Now test the full detection pipeline
    detected_objects = detector.detect_objects(test_image)
    print(f"Detected objects from pipeline: {len(detected_objects)}")
    
    # Create visualization
    vis_image = test_image.copy()
    for i, contour in enumerate(valid_contours):
        cv2.drawContours(vis_image, [contour], -1, (0, 255, 0), 2)
        # Add contour number
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(vis_image, str(i), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    cv2.imwrite("debug_contours.jpg", vis_image)
    print("✅ Contour visualization saved as debug_contours.jpg")
    
    return len(detected_objects) > 0


if __name__ == "__main__":
    success = debug_detection()
    if success:
        print("🎉 Detection working!")
    else:
        print("❌ Detection needs fixing")
