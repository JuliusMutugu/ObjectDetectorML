"""
HSV-based color analysis implementation.
"""
import cv2
import numpy as np
from typing import Dict, Tuple, List
from .color_analyzer_interface import ColorAnalyzerInterface
from ..models import Color, DetectedObject
from ..processing import ImageProcessor


class HSVColorAnalyzer(ColorAnalyzerInterface):
    """
    HSV-based color analysis implementation.
    
    This class follows the Single Responsibility Principle by focusing
    solely on HSV-based color analysis.
    """
    
    def __init__(self):
        """Initialize the HSV color analyzer with predefined color ranges."""
        self.image_processor = ImageProcessor()
        
        # Define HSV color ranges for common colors
        # Format: (lower_bound, upper_bound) where each bound is (H, S, V)
        self.color_ranges: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
            'red': ((0, 50, 50), (10, 255, 255)),
            'red2': ((170, 50, 50), (180, 255, 255)),  # Red wraps around in HSV
            'orange': ((11, 50, 50), (25, 255, 255)),
            'yellow': ((26, 50, 50), (35, 255, 255)),
            'green': ((36, 50, 50), (85, 255, 255)),
            'cyan': ((86, 50, 50), (95, 255, 255)),
            'blue': ((96, 50, 50), (125, 255, 255)),
            'purple': ((126, 50, 50), (145, 255, 255)),
            'pink': ((146, 50, 50), (169, 255, 255)),
            'white': ((0, 0, 200), (180, 30, 255)),
            'black': ((0, 0, 0), (180, 255, 50)),
            'gray': ((0, 0, 51), (180, 30, 199))
        }
        
        # Define RGB representations for colors (for visualization)
        self.color_rgb: Dict[str, Tuple[int, int, int]] = {
            'red': (255, 0, 0),
            'red2': (255, 0, 0),
            'orange': (255, 165, 0),
            'yellow': (255, 255, 0),
            'green': (0, 255, 0),
            'cyan': (0, 255, 255),
            'blue': (0, 0, 255),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128)
        }
    
    def analyze_color(self, image: np.ndarray, detected_object: DetectedObject) -> Color:
        """
        Analyze the color of a detected object using HSV color space.
        
        Args:
            image: Original image
            detected_object: Detected object to analyze
            
        Returns:
            Color: Analyzed color information
        """
        # Extract the region of interest (ROI) from the image
        roi = self._extract_roi(image, detected_object)
        
        # Convert ROI to HSV
        hsv_roi = self.image_processor.convert_to_hsv(roi)
        
        # Find the dominant color in the ROI
        dominant_color = self._find_dominant_color(hsv_roi)
        
        return dominant_color
    
    def get_supported_colors(self) -> List[str]:
        """
        Get the list of supported color names.
        
        Returns:
            List[str]: List of supported color names
        """
        # Filter out 'red2' as it's just an alternative range for red
        return [color for color in self.color_ranges.keys() if color != 'red2']
    
    def add_color_definition(self, name: str, hsv_range: tuple) -> None:
        """
        Add a new color definition.
        
        Args:
            name: Color name
            hsv_range: HSV range tuple ((h_min, s_min, v_min), (h_max, s_max, v_max))
        """
        self.color_ranges[name] = hsv_range
        # Default RGB representation (can be customized)
        self.color_rgb[name] = (128, 128, 128)
    
    def _extract_roi(self, image: np.ndarray, detected_object: DetectedObject) -> np.ndarray:
        """
        Extract the region of interest from the image.
        
        Args:
            image: Original image
            detected_object: Detected object
            
        Returns:
            np.ndarray: Extracted ROI
        """
        bbox = detected_object.bounding_box
        
        # Ensure coordinates are within image bounds
        y_start = max(0, bbox.y)
        y_end = min(image.shape[0], bbox.y + bbox.height)
        x_start = max(0, bbox.x)
        x_end = min(image.shape[1], bbox.x + bbox.width)
        
        return image[y_start:y_end, x_start:x_end]
    
    def _find_dominant_color(self, hsv_roi: np.ndarray) -> Color:
        """
        Find the dominant color in the HSV ROI.
        
        Args:
            hsv_roi: HSV region of interest
            
        Returns:
            Color: Dominant color information
        """
        best_match = None
        best_confidence = 0
        best_color_name = "unknown"
        
        for color_name, (lower, upper) in self.color_ranges.items():
            # Create mask for this color range
            mask = cv2.inRange(hsv_roi, np.array(lower), np.array(upper))
            
            # Calculate the percentage of pixels matching this color
            pixel_count = cv2.countNonZero(mask)
            total_pixels = hsv_roi.shape[0] * hsv_roi.shape[1]
            confidence = pixel_count / total_pixels if total_pixels > 0 else 0
            
            # Special handling for red (which has two ranges in HSV)
            if color_name == 'red2' and 'red' in self.color_ranges:
                # Combine with the first red range
                continue
            elif color_name == 'red':
                # Also check the second red range
                if 'red2' in self.color_ranges:
                    lower2, upper2 = self.color_ranges['red2']
                    mask2 = cv2.inRange(hsv_roi, np.array(lower2), np.array(upper2))
                    pixel_count += cv2.countNonZero(mask2)
                    confidence = pixel_count / total_pixels if total_pixels > 0 else 0
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_color_name = color_name
                best_match = mask
        
        # Get RGB values for the detected color
        if best_color_name in self.color_rgb:
            r, g, b = self.color_rgb[best_color_name]
        else:
            r, g, b = 128, 128, 128  # Default gray
        
        return Color(
            r=r,
            g=g,
            b=b,
            name=best_color_name,
            confidence=best_confidence
        )
    
    def get_average_color_in_roi(self, hsv_roi: np.ndarray) -> Tuple[int, int, int]:
        """
        Get the average HSV color in the ROI.
        
        Args:
            hsv_roi: HSV region of interest
            
        Returns:
            Tuple[int, int, int]: Average HSV values
        """
        if hsv_roi.size == 0:
            return (0, 0, 0)
        
        # Calculate mean HSV values
        mean_hsv = np.mean(hsv_roi.reshape(-1, 3), axis=0)
        return tuple(mean_hsv.astype(int))
