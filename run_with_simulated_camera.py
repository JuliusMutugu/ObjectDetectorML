"""
Simulated camera feed for demonstration when no physical camera is available.
This creates a moving object scenario to show real-time detection.
"""
import cv2
import numpy as np
import time
import random
from typing import Optional, Tuple
from camera import CameraInterface


class SimulatedCamera(CameraInterface):
    """
    Simulated camera that generates test frames with moving colored objects.
    """
    
    def __init__(self, width: int = 640, height: int = 480):
        """Initialize the simulated camera."""
        self.width = width
        self.height = height
        self.is_initialized = False
        self.frame_count = 0
        
        # Object positions and velocities
        self.objects = [
            {'pos': [100, 100], 'vel': [2, 1], 'color': (0, 0, 255), 'size': 30, 'shape': 'circle'},    # Red circle
            {'pos': [200, 150], 'vel': [-1, 2], 'color': (0, 255, 0), 'size': 40, 'shape': 'rect'},     # Green rectangle
            {'pos': [300, 200], 'vel': [1, -1], 'color': (255, 0, 0), 'size': 35, 'shape': 'circle'},   # Blue circle
            {'pos': [150, 300], 'vel': [-2, -1], 'color': (0, 255, 255), 'size': 25, 'shape': 'rect'},  # Yellow rectangle
            {'pos': [400, 100], 'vel': [1, 2], 'color': (255, 255, 0), 'size': 30, 'shape': 'circle'},   # Cyan circle
        ]
    
    def initialize(self) -> bool:
        """Initialize the simulated camera."""
        self.is_initialized = True
        return True
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Generate a frame with moving colored objects."""
        if not self.is_initialized:
            return None
        
        # Create white background
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        # Update and draw objects
        for obj in self.objects:
            # Update position
            obj['pos'][0] += obj['vel'][0]
            obj['pos'][1] += obj['vel'][1]
            
            # Bounce off walls
            if obj['pos'][0] <= obj['size'] or obj['pos'][0] >= self.width - obj['size']:
                obj['vel'][0] = -obj['vel'][0]
                obj['pos'][0] = max(obj['size'], min(self.width - obj['size'], obj['pos'][0]))
            
            if obj['pos'][1] <= obj['size'] or obj['pos'][1] >= self.height - obj['size']:
                obj['vel'][1] = -obj['vel'][1]
                obj['pos'][1] = max(obj['size'], min(self.height - obj['size'], obj['pos'][1]))
            
            # Draw object
            pos = (int(obj['pos'][0]), int(obj['pos'][1]))
            
            if obj['shape'] == 'circle':
                cv2.circle(frame, pos, obj['size'], obj['color'], -1)
                cv2.circle(frame, pos, obj['size'], (0, 0, 0), 2)  # Black border
            else:  # rectangle
                half_size = obj['size'] // 2
                pt1 = (pos[0] - half_size, pos[1] - half_size)
                pt2 = (pos[0] + half_size, pos[1] + half_size)
                cv2.rectangle(frame, pt1, pt2, obj['color'], -1)
                cv2.rectangle(frame, pt1, pt2, (0, 0, 0), 2)  # Black border
        
        # Add some noise to make it more realistic
        if self.frame_count % 30 == 0:  # Add noise every 30 frames
            noise = np.random.randint(0, 10, frame.shape, dtype=np.uint8)
            frame = cv2.add(frame, noise)
        
        # Add frame info
        cv2.putText(frame, f"Simulated Camera - Frame {self.frame_count}", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        self.frame_count += 1
        
        # Add slight delay to simulate camera frame rate
        time.sleep(0.033)  # ~30 FPS
        
        return frame
    
    def release(self) -> None:
        """Release the simulated camera."""
        self.is_initialized = False
    
    def is_opened(self) -> bool:
        """Check if the simulated camera is opened."""
        return self.is_initialized
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get the camera resolution."""
        return (self.width, self.height)


def main():
    """Run object detection with simulated camera."""
    print("🎯 Object Detection with Simulated Camera")
    print("=" * 50)
    print("🎬 Starting simulated camera feed with moving objects")
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press ESC to quit")
    print("  - Watch as colored objects move around and get detected!")
    
    # Import here to avoid circular imports
    from main import ObjectDetectionApp
    
    # Create app with simulated camera
    simulated_camera = SimulatedCamera(width=640, height=480)
    app = ObjectDetectionApp(camera=simulated_camera)
    
    # Run the app
    app.run()


if __name__ == "__main__":
    main()
