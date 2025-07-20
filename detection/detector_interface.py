"""
Object detection interface.
This module follows the Interface Segregation Principle by defining
a focused detection interface.
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import List
from ..models import DetectedObject


class DetectorInterface(ABC):
    """
    Abstract interface for object detection.
    
    This interface follows the Dependency Inversion Principle by defining
    abstractions that concrete detection implementations must follow.
    """
    
    @abstractmethod
    def detect_objects(self, image: np.ndarray) -> List[DetectedObject]:
        """
        Detect objects in the given image.
        
        Args:
            image: Input image for object detection
            
        Returns:
            List[DetectedObject]: List of detected objects
        """
        pass
    
    @abstractmethod
    def set_parameters(self, **kwargs) -> None:
        """
        Set detection parameters.
        
        Args:
            **kwargs: Parameter key-value pairs
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> dict:
        """
        Get current detection parameters.
        
        Returns:
            dict: Current parameter values
        """
        pass
