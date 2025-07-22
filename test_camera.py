"""
Comprehensive camera test for laptop built-in cameras.
This script will help diagnose and fix camera issues on Windows laptops.
"""
import cv2
import numpy as np
import subprocess
import sys
import time


def check_windows_camera_privacy():
    """Check Windows camera privacy settings."""
    print("🔒 Checking Windows Camera Privacy Settings...")
    print("Please ensure:")
    print("1. Go to Windows Settings > Privacy & Security > Camera")
    print("2. Make sure 'Camera access' is ON")
    print("3. Make sure 'Let apps access your camera' is ON") 
    print("4. Make sure 'Let desktop apps access your camera' is ON")
    print("5. If you see Python in the list, make sure it's allowed")
    input("\nPress Enter after checking these settings...")


def test_camera_with_different_backends():
    """Test camera with different OpenCV backends."""
    backends = [
        (cv2.CAP_DSHOW, "DirectShow (Windows)"),
        (cv2.CAP_MSMF, "Microsoft Media Foundation"),
        (cv2.CAP_ANY, "Any available backend"),
    ]
    
    print("\n🎥 Testing different camera backends...")
    
    for backend_id, backend_name in backends:
        print(f"\nTrying {backend_name}...")
        
        for camera_index in range(3):  # Try indices 0, 1, 2
            try:
                cap = cv2.VideoCapture(camera_index, backend_id)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ SUCCESS! Camera found at index {camera_index} with {backend_name}")
                        print(f"   Frame shape: {frame.shape}")
                        cap.release()
                        return camera_index, backend_id
                        
                cap.release()
            except Exception as e:
                print(f"❌ Error with index {camera_index}: {e}")
    
    return None, None


def test_basic_camera_access():
    """Test basic camera access."""
    print("\n🔍 Testing basic camera access...")
    
    for i in range(5):
        print(f"Testing camera index {i}...")
        try:
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {i} is working! Frame shape: {frame.shape}")
                    cap.release()
                    return i
                else:
                    print(f"❌ Camera {i} opened but can't read frames")
            else:
                print(f"❌ Camera {i} failed to open")
            
            cap.release()
        except Exception as e:
            print(f"❌ Error testing camera {i}: {e}")
    
    return None


def show_camera_preview(camera_index, backend=cv2.CAP_ANY):
    """Show a preview of the camera feed."""
    print(f"\n📹 Starting camera preview (index: {camera_index})")
    print("Press 'q' to quit the preview")
    
    cap = cv2.VideoCapture(camera_index, backend)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("❌ Failed to open camera for preview")
        return False
    
    cv2.namedWindow("Camera Test Preview", cv2.WINDOW_AUTOSIZE)
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Add frame info
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"Camera {camera_index} - FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Camera Test Preview", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Camera preview completed")
    return True


def update_camera_config(camera_index):
    """Update the camera configuration file."""
    config_path = "config/detection_config.yaml"
    
    try:
        with open(config_path, 'r') as file:
            content = file.read()
        
        # Replace camera index
        import re
        content = re.sub(r'index:\s*\d+', f'index: {camera_index}', content)
        
        with open(config_path, 'w') as file:
            file.write(content)
        
        print(f"✅ Updated camera index to {camera_index} in config file")
    except Exception as e:
        print(f"⚠️ Warning: Could not update config file: {e}")


def main():
    """Main camera test function."""
    print("🎯 Laptop Camera Diagnostic Tool")
    print("=" * 50)
    
    # Step 1: Check privacy settings
    check_windows_camera_privacy()
    
    # Step 2: Test basic camera access
    camera_index = test_basic_camera_access()
    
    if camera_index is not None:
        print(f"\n🎉 Basic camera test successful! Camera found at index {camera_index}")
        
        # Step 3: Show preview
        response = input(f"\nWould you like to see a camera preview? (y/n): ")
        if response.lower() in ['y', 'yes']:
            show_camera_preview(camera_index)
        
        # Step 4: Update config and test object detection
        update_camera_config(camera_index)
        
        response = input(f"\nWould you like to test with object detection? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print("Starting object detection app...")
            return True
    
    else:
        print("\n❌ No working camera found!")
        print("\nTroubleshooting steps:")
        print("1. Check Device Manager for camera devices")
        print("2. Make sure camera privacy settings are correct")
        print("3. Close other applications that might be using the camera")
        print("4. Check if camera works in Windows Camera app")
        print("5. Restart your computer")
        
        # Try advanced backends
        print("\nTrying advanced backend detection...")
        camera_index, backend = test_camera_with_different_backends()
        
        if camera_index is not None:
            print(f"\n🎉 Found camera with advanced detection!")
            print(f"Camera index: {camera_index}, Backend: {backend}")
            
            response = input("Would you like to test this camera? (y/n): ")
            if response.lower() in ['y', 'yes']:
                if show_camera_preview(camera_index, backend):
                    update_camera_config(camera_index)
                    return True
    
    return False


if __name__ == "__main__":
    if main():
        print("\n🚀 Now running the object detection app...")
        try:
            import subprocess
            subprocess.run([sys.executable, "main.py"])
        except Exception as e:
            print(f"Error running main app: {e}")
    else:
        print("\n❌ Camera setup failed. Please follow the troubleshooting steps above.")
