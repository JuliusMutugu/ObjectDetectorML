"""
HSV-based color analysis implementation.
"""
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Dict, Tuple, List
from .color_analyzer_interface import ColorAnalyzerInterface
from models import Color, DetectedObject
from processing import ImageProcessor


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
        Find the dominant color in the HSV ROI with improved accuracy.
        
        Args:
            hsv_roi: HSV region of interest
            
        Returns:
            Color: Dominant color information
        """
        if hsv_roi.size == 0:
            return Color(128, 128, 128, "unknown", 0.0)
        
        # Apply noise reduction
        hsv_roi_filtered = cv2.medianBlur(hsv_roi, 5)
        
        # Calculate histogram for better color analysis
        hist_h = cv2.calcHist([hsv_roi_filtered], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv_roi_filtered], [1], None, [256], [0, 256])
        hist_v = cv2.calcHist([hsv_roi_filtered], [2], None, [256], [0, 256])
        
        # Get dominant hue
        dominant_hue = np.argmax(hist_h)
        
        best_match = None
        best_confidence = 0
        best_color_name = "unknown"
        color_scores = {}
        
        for color_name, (lower, upper) in self.color_ranges.items():
            # Create mask for this color range
            mask = cv2.inRange(hsv_roi_filtered, np.array(lower), np.array(upper))
            
            # Calculate the percentage of pixels matching this color
            pixel_count = cv2.countNonZero(mask)
            total_pixels = hsv_roi_filtered.shape[0] * hsv_roi_filtered.shape[1]
            base_confidence = pixel_count / total_pixels if total_pixels > 0 else 0
            
            # Special handling for red (which has two ranges in HSV)
            if color_name == 'red2' and 'red' in self.color_ranges:
                # Combine with the first red range
                continue
            elif color_name == 'red':
                # Also check the second red range
                if 'red2' in self.color_ranges:
                    lower2, upper2 = self.color_ranges['red2']
                    mask2 = cv2.inRange(hsv_roi_filtered, np.array(lower2), np.array(upper2))
                    pixel_count += cv2.countNonZero(mask2)
                    base_confidence = pixel_count / total_pixels if total_pixels > 0 else 0
            
            # Apply histogram-based confidence boost
            hue_range = range(lower[0], upper[0] + 1)
            if dominant_hue in hue_range:
                base_confidence *= 1.2  # Boost confidence if dominant hue matches
            
            # Consider saturation and value for better detection
            mean_s = np.mean(hsv_roi_filtered[:, :, 1])
            mean_v = np.mean(hsv_roi_filtered[:, :, 2])
            
            # Adjust confidence based on saturation and brightness
            if mean_s > 50 and mean_v > 50:  # Good color conditions
                base_confidence *= 1.1
            elif mean_s < 30:  # Low saturation (grayish)
                if color_name in ['white', 'black', 'gray']:
                    base_confidence *= 1.2
                else:
                    base_confidence *= 0.8
            elif mean_v < 50:  # Low brightness
                if color_name == 'black':
                    base_confidence *= 1.3
                else:
                    base_confidence *= 0.9
            elif mean_v > 200:  # High brightness
                if color_name == 'white':
                    base_confidence *= 1.3
                else:
                    base_confidence *= 0.9
            
            color_scores[color_name] = base_confidence
            
            if base_confidence > best_confidence:
                best_confidence = base_confidence
                best_color_name = color_name
                best_match = mask
        
        # Additional validation: check if confidence is too low
        if best_confidence < 0.1:
            # Analyze average color if no clear match
            mean_hsv = self.get_average_color_in_roi(hsv_roi_filtered)
            best_color_name = self._classify_by_average_hsv(mean_hsv)
            best_confidence = 0.5  # Medium confidence for average-based classification
        
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
            confidence=min(best_confidence, 1.0)  # Cap at 1.0
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
    
    def _classify_by_average_hsv(self, hsv_values: Tuple[int, int, int]) -> str:
        """
        Classify color based on average HSV values.
        
        Args:
            hsv_values: Average HSV values (H, S, V)
            
        Returns:
            str: Color name
        """
        h, s, v = hsv_values
        
        # Handle grayscale colors based on saturation and value
        if s < 30:  # Low saturation - grayscale
            if v < 50:
                return "black"
            elif v > 200:
                return "white"
            else:
                return "gray"
        
        # Handle colored objects based on hue
        if h <= 10 or h >= 170:
            return "red"
        elif 11 <= h <= 25:
            return "orange"
        elif 26 <= h <= 35:
            return "yellow"
        elif 36 <= h <= 85:
            return "green"
        elif 86 <= h <= 95:
            return "cyan"
        elif 96 <= h <= 125:
            return "blue"
        elif 126 <= h <= 145:
            return "purple"
        elif 146 <= h <= 169:
            return "pink"
        else:
            return "unknown"
