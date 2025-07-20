"""
Camera interface and implementations.
This module follows the Interface Segregation Principle by defining
a focused camera interface.
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Tuple


class CameraInterface(ABC):
    """
    Abstract interface for camera operations.
    
    This interface follows the Dependency Inversion Principle by defining
    abstractions that concrete implementations must follow.
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the camera.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.
        
        Returns:
            Optional[np.ndarray]: The captured frame, or None if capture failed
        """
        pass
    
    @abstractmethod
    def release(self) -> None:
        """Release the camera resources."""
        pass
    
    @abstractmethod
    def is_opened(self) -> bool:
        """
        Check if the camera is opened and ready.
        
        Returns:
            bool: True if camera is ready, False otherwise
        """
        pass
    
    @abstractmethod
    def get_resolution(self) -> Tuple[int, int]:
        """
        Get the camera resolution.
        
        Returns:
            Tuple[int, int]: Width and height of the camera
        """
        pass
