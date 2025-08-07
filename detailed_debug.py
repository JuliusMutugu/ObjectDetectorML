"""
Detailed debug script for detection pipeline.
"""
import cv2
import numpy as np
from detection import ContourDetector


def debug_detector_pipeline():
    """Debug each step of the detector pipeline."""
    print("🔍 Detailed Detection Pipeline Debug")
    print("=" * 50)
    
    # Create simple test image
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.circle(image, (150, 200), 80, (255, 255, 255), -1)
    cv2.rectangle(image, (300, 120), (450, 280), (255, 255, 255), -1)
    
    print("✅ Created test image with circle and rectangle")
    
    # Initialize detector
    detector = ContourDetector(min_contour_area=100, max_contour_area=100000)
    
    # Step 1: Preprocess
    print("\n📊 Step 1: Preprocessing...")
    processed = detector._preprocess_image(image)
    cv2.imwrite("debug_processed.jpg", processed)
    print(f"   Processed image shape: {processed.shape}")
    print(f"   Processed image type: {processed.dtype}")
    print(f"   Unique values in processed: {np.unique(processed)}")
    
    # Step 2: Find contours
    print("\n📊 Step 2: Finding contours...")
    contours = detector._find_contours(processed)
    print(f"   Found {len(contours)} contours")
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        print(f"   Contour {i}: area = {area}")
    
    # Step 3: Validate contours
    print("\n📊 Step 3: Validating contours...")
    valid_contours = []
    for i, contour in enumerate(contours):
        is_valid = detector._is_valid_contour(contour)
        area = cv2.contourArea(contour)
        print(f"   Contour {i}: area = {area}, valid = {is_valid}")
        if is_valid:
            valid_contours.append(contour)
    
    print(f"   Valid contours: {len(valid_contours)}")
    
    # Step 4: Convert to objects
    print("\n📊 Step 4: Converting to DetectedObjects...")
    objects = []
    for i, contour in enumerate(valid_contours):
        try:
            obj = detector._contour_to_detected_object(contour)
            objects.append(obj)
            print(f"   Object {i}: area = {obj.area}, confidence = {obj.confidence}")
        except Exception as e:
            print(f"   Error converting contour {i}: {e}")
    
    print(f"\n✅ Final result: {len(objects)} DetectedObjects")
    
    # Test full pipeline
    print("\n📊 Testing full pipeline...")
    detected_objects = detector.detect_objects(image)
    print(f"   Full pipeline result: {len(detected_objects)} objects")
    
    return len(detected_objects) > 0


if __name__ == "__main__":
    success = debug_detector_pipeline()
    if success:
        print("\n🎉 Detection working!")
    else:
        print("\n❌ Detection still needs fixing")
