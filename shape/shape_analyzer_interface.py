"""
Shape analysis interface.
This module follows the Interface Segregation Principle by defining
a focused shape analysis interface.
"""
from abc import ABC, abstractmethod
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List
from models import Shape, DetectedObject


class ShapeAnalyzerInterface(ABC):
    """
    Abstract interface for shape analysis.
    
    This interface follows the Dependency Inversion Principle by defining
    abstractions that concrete shape analysis implementations must follow.
    """
    
    @abstractmethod
    def analyze_shape(self, detected_object: DetectedObject) -> Shape:
        """
        Analyze the shape of a detected object.
        
        Args:
            detected_object: Detected object to analyze
            
        Returns:
            Shape: Analyzed shape information
        """
        pass
    
    @abstractmethod
    def get_supported_shapes(self) -> List[str]:
        """
        Get the list of supported shape names.
        
        Returns:
            List[str]: List of supported shape names
        """
        pass
    
    @abstractmethod
    def classify_contour(self, contour: np.ndarray) -> str:
        """
        Classify a contour into a shape category.
        
        Args:
            contour: Contour to classify
            
        Returns:
            str: Shape name
        """
        pass
