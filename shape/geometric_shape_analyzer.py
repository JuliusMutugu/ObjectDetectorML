"""
Geometric shape analysis implementation.
"""
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List
from .shape_analyzer_interface import ShapeAnalyzerInterface
from models import Shape, DetectedObject


class GeometricShapeAnalyzer(ShapeAnalyzerInterface):
    """
    Geometric shape analysis implementation.
    
    This class follows the Single Responsibility Principle by focusing
    solely on geometric shape analysis.
    """
    
    def __init__(self):
        """Initialize the geometric shape analyzer."""
        self.supported_shapes = [
            'circle', 'triangle', 'rectangle', 'square', 
            'pentagon', 'hexagon', 'polygon', 'unknown'
        ]
    
    def analyze_shape(self, detected_object: DetectedObject) -> Shape:
        """
        Analyze the shape of a detected object.
        
        Args:
            detected_object: Detected object to analyze
            
        Returns:
            Shape: Analyzed shape information
        """
        contour = detected_object.contour
        bbox = detected_object.bounding_box
        
        # Calculate basic shape properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Calculate area ratio (contour area / bounding box area)
        bbox_area = bbox.width * bbox.height
        area_ratio = area / bbox_area if bbox_area > 0 else 0
        
        # Calculate aspect ratio
        aspect_ratio = bbox.width / bbox.height if bbox.height > 0 else 0
        
        # Classify the shape
        shape_name = self.classify_contour(contour)
        
        # Calculate confidence based on how well the shape fits the classification
        confidence = self._calculate_shape_confidence(contour, shape_name, area_ratio, aspect_ratio)
        
        # Count vertices for polygon shapes
        vertices = self._count_vertices(contour)
        
        return Shape(
            name=shape_name,
            confidence=confidence,
            vertices=vertices,
            area_ratio=area_ratio,
            aspect_ratio=aspect_ratio
        )
    
    def get_supported_shapes(self) -> List[str]:
        """
        Get the list of supported shape names.
        
        Returns:
            List[str]: List of supported shape names
        """
        return self.supported_shapes.copy()
    
    def classify_contour(self, contour: np.ndarray) -> str:
        """
        Classify a contour into a shape category.
        
        Args:
            contour: Contour to classify
            
        Returns:
            str: Shape name
        """
        # Approximate contour to reduce noise
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        vertices = len(approx)
        
        # Calculate area and perimeter
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if area < 100:  # Too small to classify reliably
            return "unknown"
        
        # Calculate circularity (4π * area / perimeter²)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Get bounding rectangle for aspect ratio
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # Classify based on vertices and other properties
        if circularity > 0.75:
            return "circle"
        elif vertices == 3:
            return "triangle"
        elif vertices == 4:
            # Distinguish between square and rectangle
            if 0.9 <= aspect_ratio <= 1.1:
                return "square"
            else:
                return "rectangle"
        elif vertices == 5:
            return "pentagon"
        elif vertices == 6:
            return "hexagon"
        elif vertices > 6:
            return "polygon"
        else:
            # Additional analysis for complex shapes
            if circularity > 0.6:
                return "circle"
            elif 4 <= vertices <= 6:
                return "polygon"
            else:
                return "unknown"
    
    def _count_vertices(self, contour: np.ndarray) -> int:
        """
        Count vertices in a contour.
        
        Args:
            contour: Input contour
            
        Returns:
            int: Number of vertices
        """
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        return len(approx)
    
    def _calculate_shape_confidence(self, contour: np.ndarray, shape_name: str, 
                                   area_ratio: float, aspect_ratio: float) -> float:
        """
        Calculate confidence score for shape classification.
        
        Args:
            contour: Input contour
            shape_name: Classified shape name
            area_ratio: Ratio of contour area to bounding box area
            aspect_ratio: Width to height ratio
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Calculate circularity
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        if shape_name == "circle":
            # High circularity increases confidence for circles
            confidence = min(circularity * 1.2, 1.0)
        elif shape_name == "square":
            # Good aspect ratio and area ratio increase confidence for squares
            if 0.9 <= aspect_ratio <= 1.1:
                confidence += 0.3
            if area_ratio > 0.8:
                confidence += 0.2
        elif shape_name == "rectangle":
            # Good area ratio increases confidence for rectangles
            if area_ratio > 0.8:
                confidence += 0.3
            if aspect_ratio < 0.9 or aspect_ratio > 1.1:
                confidence += 0.2
        elif shape_name == "triangle":
            # Triangles should have lower area ratio
            if 0.4 <= area_ratio <= 0.6:
                confidence += 0.3
        elif shape_name in ["pentagon", "hexagon", "polygon"]:
            # Regular polygons should have good area ratio
            if area_ratio > 0.7:
                confidence += 0.2
        
        return min(confidence, 1.0)
