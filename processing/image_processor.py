"""
Image processing utilities.
This module follows the Single Responsibility Principle by focusing
on image preprocessing operations.
"""
import cv2
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """
    Handles image preprocessing operations.
    
    This class follows the Single Responsibility Principle by focusing
    solely on image processing tasks.
    """
    
    @staticmethod
    def resize_image(image: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        Resize an image to specified dimensions.
        
        Args:
            image: Input image
            width: Target width
            height: Target height
            
        Returns:
            np.ndarray: Resized image
        """
        return cv2.resize(image, (width, height))
    
    @staticmethod
    def convert_to_hsv(image: np.ndarray) -> np.ndarray:
        """
        Convert BGR image to HSV color space.
        
        Args:
            image: BGR image
            
        Returns:
            np.ndarray: HSV image
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    @staticmethod
    def convert_to_gray(image: np.ndarray) -> np.ndarray:
        """
        Convert BGR image to grayscale.
        
        Args:
            image: BGR image
            
        Returns:
            np.ndarray: Grayscale image
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply Gaussian blur to reduce noise.
        
        Args:
            image: Input image
            kernel_size: Size of the Gaussian kernel (must be odd)
            
        Returns:
            np.ndarray: Blurred image
        """
        if kernel_size % 2 == 0:
            kernel_size += 1  # Ensure odd kernel size
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    @staticmethod
    def apply_morphological_operations(mask: np.ndarray, 
                                     operation: str = 'opening',
                                     kernel_size: int = 5) -> np.ndarray:
        """
        Apply morphological operations to clean up the mask.
        
        Args:
            mask: Binary mask
            operation: Type of operation ('opening', 'closing', 'erosion', 'dilation')
            kernel_size: Size of the morphological kernel
            
        Returns:
            np.ndarray: Processed mask
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        if operation == 'opening':
            return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        elif operation == 'closing':
            return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        elif operation == 'erosion':
            return cv2.erode(mask, kernel, iterations=1)
        elif operation == 'dilation':
            return cv2.dilate(mask, kernel, iterations=1)
        else:
            return mask
    
    @staticmethod
    def create_color_mask(hsv_image: np.ndarray, 
                         lower_bound: Tuple[int, int, int],
                         upper_bound: Tuple[int, int, int]) -> np.ndarray:
        """
        Create a binary mask for a specific color range.
        
        Args:
            hsv_image: HSV image
            lower_bound: Lower HSV bound (H, S, V)
            upper_bound: Upper HSV bound (H, S, V)
            
        Returns:
            np.ndarray: Binary mask
        """
        return cv2.inRange(hsv_image, np.array(lower_bound), np.array(upper_bound))
    
    @staticmethod
    def enhance_contrast(image: np.ndarray, alpha: float = 1.5, beta: int = 0) -> np.ndarray:
        """
        Enhance image contrast and brightness.
        
        Args:
            image: Input image
            alpha: Contrast control (1.0-3.0)
            beta: Brightness control (0-100)
            
        Returns:
            np.ndarray: Enhanced image
        """
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    @staticmethod
    def apply_bilateral_filter(image: np.ndarray, d: int = 9, 
                             sigma_color: int = 75, sigma_space: int = 75) -> np.ndarray:
        """
        Apply bilateral filter to reduce noise while preserving edges.
        
        Args:
            image: Input image
            d: Diameter of pixel neighborhood
            sigma_color: Filter sigma in the color space
            sigma_space: Filter sigma in the coordinate space
            
        Returns:
            np.ndarray: Filtered image
        """
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
