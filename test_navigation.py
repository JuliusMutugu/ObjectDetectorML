"""
Simple test for the blind navigation assistant.
"""
import cv2
import numpy as np
from blind_navigation_assistant import NavigationAssistant, BlindNavigationApp


def test_navigation_audio():
    """Test the navigation assistant audio system."""
    print("🎯 Testing Navigation Assistant Audio System")
    print("=" * 50)
    
    # Initialize navigation assistant
    nav_assistant = NavigationAssistant()
    
    # Test TTS system
    if nav_assistant.tts_engine:
        print("✅ Text-to-speech system initialized")
        print("🔊 Testing audio feedback...")
        
        # Test basic announcement
        nav_assistant._speak_message("Navigation assistant ready")
        
        # Test navigation feedback
        test_messages = [
            "Red circle directly ahead",
            "Blue rectangle on the left", 
            "Path ahead is clear",
            "CAUTION: Obstacle directly ahead"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"🔊 Playing message {i+1}: {message}")
            nav_assistant._speak_message(message)
            import time
            time.sleep(2)  # Pause between messages
            
        print("✅ Audio test completed")
    else:
        print("❌ Text-to-speech not available")
    
    return nav_assistant.tts_engine is not None


def test_zone_detection():
    """Test zone-based object detection."""
    print("\n🎯 Testing Zone-based Detection")
    print("=" * 50)
    
    # Create test navigation assistant
    nav_assistant = NavigationAssistant()
    
    # Create mock detection result with objects in different zones
    from models import DetectedObject, BoundingBox, Color, Shape, DetectionResult
    
    # Create test objects
    test_objects = [
        # Object in immediate center (critical zone)
        DetectedObject(
            bounding_box=BoundingBox(300, 400, 80, 60),
            contour=np.array([[300, 400], [380, 400], [380, 460], [300, 460]]),
            color=Color(255, 0, 0, "red", 0.9),
            shape=Shape("rectangle", 0.8, 4, 0.85, 1.33)
        ),
        
        # Object in immediate left (high priority)
        DetectedObject(
            bounding_box=BoundingBox(100, 350, 60, 60),
            contour=np.array([[100, 350], [160, 350], [160, 410], [100, 410]]),
            color=Color(0, 255, 0, "green", 0.95),
            shape=Shape("square", 0.95, 4, 0.9, 1.0)
        ),
        
        # Object in far right (medium priority)
        DetectedObject(
            bounding_box=BoundingBox(500, 200, 70, 50),
            contour=np.array([[500, 200], [570, 200], [570, 250], [500, 250]]),
            color=Color(0, 0, 255, "blue", 0.85),
            shape=Shape("rectangle", 0.75, 4, 0.8, 1.4)
        )
    ]
    
    # Create mock frame
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Create detection result
    detection_result = DetectionResult(
        objects=test_objects,
        frame=test_frame,
        timestamp=1234567890.0
    )
    
    # Analyze scene
    analysis = nav_assistant.analyze_scene(detection_result)
    
    print(f"📊 Analysis Results:")
    print(f"   Total objects: {analysis['total_objects']}")
    print(f"   Zones with objects: {len(analysis['zone_analysis'])}")
    
    for zone, zone_data in analysis['zone_analysis'].items():
        print(f"   {zone}: {zone_data['object_count']} objects ({zone_data['priority']} priority)")
    
    print(f"\n🧭 Navigation Advice:")
    for advice in analysis['navigation_advice']:
        print(f"   • {advice}")
    
    print(f"\n⚠️  Warnings:")
    for warning in analysis['warnings']:
        print(f"   • {warning}")
    
    # Test audio feedback
    if nav_assistant.tts_engine:
        print(f"\n🔊 Providing audio feedback...")
        nav_assistant.provide_audio_feedback(analysis)
    
    return True


def main():
    """Main test function."""
    print("🎯 Blind Navigation Assistant - Test Suite")
    print("=" * 60)
    
    # Test 1: Audio system
    audio_success = test_navigation_audio()
    
    # Test 2: Zone detection
    zone_success = test_zone_detection()
    
    print(f"\n📊 Test Results:")
    print(f"   Audio System: {'✅ PASS' if audio_success else '❌ FAIL'}")
    print(f"   Zone Detection: {'✅ PASS' if zone_success else '❌ FAIL'}")
    
    if audio_success and zone_success:
        print(f"\n🎉 All tests passed! Ready to run full navigation assistant.")
        
        response = input(f"\nWould you like to run the full navigation assistant? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print(f"\n🚀 Starting Blind Navigation Assistant...")
            app = BlindNavigationApp()
            app.run()
    else:
        print(f"\n⚠️  Some tests failed. Please check the system.")


if __name__ == "__main__":
    main()
