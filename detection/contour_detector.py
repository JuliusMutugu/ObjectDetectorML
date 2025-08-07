"""
Contour-based object detection implementation.
"""
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Tuple
from .detector_interface import DetectorInterface
from models import DetectedObject, BoundingBox
from processing import ImageProcessor


class ContourDetector(DetectorInterface):
    """
    Contour-based object detection implementation.
    
    This class follows the Single Responsibility Principle by focusing
    solely on contour-based object detection.
    """
    
    def __init__(self, 
                 min_contour_area: int = 500,
                 max_contour_area: int = 50000,
                 blur_kernel_size: int = 5,
                 morph_kernel_size: int = 5):
        """
        Initialize the contour detector.
        
        Args:
            min_contour_area: Minimum area for valid contours
            max_contour_area: Maximum area for valid contours
            blur_kernel_size: Kernel size for Gaussian blur
            morph_kernel_size: Kernel size for morphological operations
        """
        self.min_contour_area = min_contour_area
        self.max_contour_area = max_contour_area
        self.blur_kernel_size = blur_kernel_size
        self.morph_kernel_size = morph_kernel_size
        self.image_processor = ImageProcessor()
    
    def detect_objects(self, image: np.ndarray) -> List[DetectedObject]:
        """
        Detect objects using contour detection.
        
        Args:
            image: Input image for object detection
            
        Returns:
            List[DetectedObject]: List of detected objects
        """
        # Preprocess the image
        processed_image = self._preprocess_image(image)
        
        # Find contours
        contours = self._find_contours(processed_image)
        
        # Filter and convert contours to DetectedObject instances
        detected_objects = []
        for contour in contours:
            if self._is_valid_contour(contour):
                detected_object = self._contour_to_detected_object(contour)
                detected_objects.append(detected_object)
        
        return detected_objects
    
    def set_parameters(self, **kwargs) -> None:
        """
        Set detection parameters.
        
        Args:
            **kwargs: Parameter key-value pairs
        """
        if 'min_contour_area' in kwargs:
            self.min_contour_area = kwargs['min_contour_area']
        if 'max_contour_area' in kwargs:
            self.max_contour_area = kwargs['max_contour_area']
        if 'blur_kernel_size' in kwargs:
            self.blur_kernel_size = kwargs['blur_kernel_size']
        if 'morph_kernel_size' in kwargs:
            self.morph_kernel_size = kwargs['morph_kernel_size']
    
    def get_parameters(self) -> dict:
        """
        Get current detection parameters.
        
        Returns:
            dict: Current parameter values
        """
        return {
            'min_contour_area': self.min_contour_area,
            'max_contour_area': self.max_contour_area,
            'blur_kernel_size': self.blur_kernel_size,
            'morph_kernel_size': self.morph_kernel_size
        }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for contour detection.
        
        Args:
            image: Input image
            
        Returns:
            np.ndarray: Preprocessed image
        """
        # Convert to grayscale
        gray = self.image_processor.convert_to_gray(image)
        
        # Apply Gaussian blur to reduce noise
        blurred = self.image_processor.apply_gaussian_blur(gray, self.blur_kernel_size)
        
        # Use simple binary threshold for clear separation
        _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
        
        # For colored objects on white background, invert the binary image
        # This ensures objects are white (255) and background is black (0)
        mean_val = np.mean(binary)
        if mean_val > 127:  # Mostly white background
            binary = cv2.bitwise_not(binary)
        
        # Light morphological operations to clean up small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def _find_contours(self, processed_image: np.ndarray) -> List[np.ndarray]:
        """
        Find contours in the processed image.
        
        Args:
            processed_image: Preprocessed binary image
            
        Returns:
            List[np.ndarray]: List of contours
        """
        contours, _ = cv2.findContours(
            processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return list(contours)
    
    def _is_valid_contour(self, contour: np.ndarray) -> bool:
        """
        Check if a contour is valid based on area constraints.
        
        Args:
            contour: Contour to validate
            
        Returns:
            bool: True if contour is valid, False otherwise
        """
        area = cv2.contourArea(contour)
        return self.min_contour_area <= area <= self.max_contour_area
    
    def _contour_to_detected_object(self, contour: np.ndarray) -> DetectedObject:
        """
        Convert a contour to a DetectedObject.
        
        Args:
            contour: Input contour
            
        Returns:
            DetectedObject: Detected object instance
        """
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        bounding_box = BoundingBox(x, y, w, h)
        
        # Calculate confidence based on contour properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        confidence = min(circularity * 2, 1.0)  # Normalize to [0, 1]
        
        return DetectedObject(
            bounding_box=bounding_box,
            contour=contour,
            confidence=confidence
        )
