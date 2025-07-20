"""
Color analysis interface.
This module follows the Interface Segregation Principle by defining
a focused color analysis interface.
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import List
from ..models import Color, DetectedObject


class ColorAnalyzerInterface(ABC):
    """
    Abstract interface for color analysis.
    
    This interface follows the Dependency Inversion Principle by defining
    abstractions that concrete color analysis implementations must follow.
    """
    
    @abstractmethod
    def analyze_color(self, image: np.ndarray, detected_object: DetectedObject) -> Color:
        """
        Analyze the color of a detected object.
        
        Args:
            image: Original image
            detected_object: Detected object to analyze
            
        Returns:
            Color: Analyzed color information
        """
        pass
    
    @abstractmethod
    def get_supported_colors(self) -> List[str]:
        """
        Get the list of supported color names.
        
        Returns:
            List[str]: List of supported color names
        """
        pass
    
    @abstractmethod
    def add_color_definition(self, name: str, hsv_range: tuple) -> None:
        """
        Add a new color definition.
        
        Args:
            name: Color name
            hsv_range: HSV range tuple ((h_min, s_min, v_min), (h_max, s_max, v_max))
        """
        pass
