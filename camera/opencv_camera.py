"""
OpenCV camera implementation.
"""
import cv2
import numpy as np
from typing import Optional, Tuple
from .camera_interface import CameraInterface


class OpenCVCamera(CameraInterface):
    """
    OpenCV implementation of the camera interface.
    
    This class follows the Single Responsibility Principle by focusing
    solely on camera operations using OpenCV.
    """
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize the OpenCV camera.
        
        Args:
            camera_index: Index of the camera to use (default: 0)
            width: Desired frame width (default: 640)
            height: Desired frame height (default: 480)
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
    
    def initialize(self) -> bool:
        """
        Initialize the camera with OpenCV.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.
        
        Returns:
            Optional[np.ndarray]: The captured frame, or None if capture failed
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    
    def release(self) -> None:
        """Release the camera resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def is_opened(self) -> bool:
        """
        Check if the camera is opened and ready.
        
        Returns:
            bool: True if camera is ready, False otherwise
        """
        return self.cap is not None and self.cap.isOpened()
    
    def get_resolution(self) -> Tuple[int, int]:
        """
        Get the camera resolution.
        
        Returns:
            Tuple[int, int]: Width and height of the camera
        """
        if not self.cap or not self.cap.isOpened():
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
