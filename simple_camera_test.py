"""
Simple camera test for laptop built-in camera.
"""
import cv2

print("🎯 Simple Laptop Camera Test")
print("=" * 30)

# First, let's check if we can find any camera
found_camera = False
working_index = None

for i in range(3):
    print(f"Testing camera index {i}...")
    
    try:
        # Try with DirectShow backend (Windows specific)
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ SUCCESS! Found working camera at index {i}")
                print(f"Frame shape: {frame.shape}")
                working_index = i
                found_camera = True
                cap.release()
                break
            else:
                print(f"❌ Camera {i} opened but can't read frames")
        else:
            print(f"❌ Camera {i} failed to open")
        
        cap.release()
        
    except Exception as e:
        print(f"❌ Error with camera {i}: {e}")

if found_camera:
    print(f"\n🎉 Camera found at index {working_index}!")
    
    # Update the config file
    try:
        config_path = "config/detection_config.yaml"
        with open(config_path, 'r') as file:
            content = file.read()
        
        import re
        content = re.sub(r'index:\s*\d+', f'index: {working_index}', content)
        
        with open(config_path, 'w') as file:
            file.write(content)
        
        print(f"✅ Updated config to use camera index {working_index}")
        
        print("\n🚀 Now you can run: python main.py")
        
    except Exception as e:
        print(f"⚠️ Could not update config: {e}")
        print(f"Please manually change 'index: 0' to 'index: {working_index}' in config/detection_config.yaml")

else:
    print("\n❌ No camera found!")
    print("Troubleshooting steps:")
    print("1. Go to Windows Settings > Privacy & Security > Camera")
    print("2. Make sure camera access is enabled")
    print("3. Make sure 'Let desktop apps access your camera' is ON")
    print("4. Close any other apps using the camera (Teams, Zoom, etc.)")
    print("5. Try opening Windows Camera app to see if camera works there")

input("\nPress Enter to continue...")
