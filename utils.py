"""
Utility functions for the object detection system.
"""
import cv2
import numpy as np
from typing import List, Tuple
from models import DetectedObject, Color


class VisualizationUtils:
    """
    Utility class for visualization functions.
    
    This class follows the Single Responsibility Principle by focusing
    solely on visualization utilities.
    """
    
    @staticmethod
    def draw_object_info(frame: np.ndarray, 
                        detected_object: DetectedObject,
                        show_id: bool = True,
                        show_area: bool = True,
                        show_confidence: bool = True) -> np.ndarray:
        """
        Draw detailed information about a detected object.
        
        Args:
            frame: Image frame to draw on
            detected_object: Object to visualize
            show_id: Whether to show object ID
            show_area: Whether to show object area
            show_confidence: Whether to show confidence score
            
        Returns:
            np.ndarray: Frame with object information drawn
        """
        result_frame = frame.copy()
        bbox = detected_object.bounding_box
        
        # Prepare info lines
        info_lines = []
        if show_id and detected_object.object_id is not None:
            info_lines.append(f"ID: {detected_object.object_id}")
        if show_area:
            info_lines.append(f"Area: {detected_object.area}")
        if show_confidence:
            info_lines.append(f"Conf: {detected_object.confidence:.2f}")
        if detected_object.color:
            info_lines.append(f"Color: {detected_object.color.name}")
        
        # Draw info
        y_offset = bbox.y + bbox.height + 20
        for line in info_lines:
            cv2.putText(result_frame, line, (bbox.x, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 15
        
        return result_frame
    
    @staticmethod
    def create_color_palette(colors: List[Color], 
                           palette_width: int = 300, 
                           palette_height: int = 50) -> np.ndarray:
        """
        Create a color palette visualization.
        
        Args:
            colors: List of colors to display
            palette_width: Width of the palette
            palette_height: Height of the palette
            
        Returns:
            np.ndarray: Color palette image
        """
        if not colors:
            return np.zeros((palette_height, palette_width, 3), dtype=np.uint8)
        
        palette = np.zeros((palette_height, palette_width, 3), dtype=np.uint8)
        segment_width = palette_width // len(colors)
        
        for i, color in enumerate(colors):
            x_start = i * segment_width
            x_end = min((i + 1) * segment_width, palette_width)
            palette[:, x_start:x_end] = color.to_bgr_tuple()
            
            # Add color name
            text_x = x_start + 5
            text_y = palette_height // 2
            cv2.putText(palette, color.name, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return palette


class MathUtils:
    """
    Mathematical utility functions.
    
    This class follows the Single Responsibility Principle by focusing
    solely on mathematical computations.
    """
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            float: Euclidean distance
        """
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    @staticmethod
    def calculate_contour_properties(contour: np.ndarray) -> dict:
        """
        Calculate various properties of a contour.
        
        Args:
            contour: Input contour
            
        Returns:
            dict: Dictionary with contour properties
        """
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Calculate circularity
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Calculate compactness
        compactness = area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Calculate aspect ratio
        _, _, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # Calculate extent (ratio of contour area to bounding rectangle area)
        rect_area = w * h
        extent = area / rect_area if rect_area > 0 else 0
        
        return {
            'area': area,
            'perimeter': perimeter,
            'circularity': circularity,
            'compactness': compactness,
            'aspect_ratio': aspect_ratio,
            'extent': extent
        }


class ColorUtils:
    """
    Color manipulation utilities.
    
    This class follows the Single Responsibility Principle by focusing
    solely on color-related operations.
    """
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, int, int]:
        """
        Convert RGB to HSV color space.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            Tuple[int, int, int]: HSV values
        """
        # Normalize RGB values
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val
        
        # Calculate Value
        v = max_val
        
        # Calculate Saturation
        s = diff / max_val if max_val != 0 else 0
        
        # Calculate Hue
        if diff == 0:
            h = 0
        elif max_val == r_norm:
            h = (60 * ((g_norm - b_norm) / diff) + 360) % 360
        elif max_val == g_norm:
            h = (60 * ((b_norm - r_norm) / diff) + 120) % 360
        else:  # max_val == b_norm
            h = (60 * ((r_norm - g_norm) / diff) + 240) % 360
        
        return (int(h / 2), int(s * 255), int(v * 255))  # OpenCV HSV ranges
    
    @staticmethod
    def is_color_similar(color1: Color, color2: Color, threshold: float = 0.3) -> bool:
        """
        Check if two colors are similar based on their RGB values.
        
        Args:
            color1: First color
            color2: Second color
            threshold: Similarity threshold (0-1)
            
        Returns:
            bool: True if colors are similar, False otherwise
        """
        # Calculate color distance in RGB space
        distance = np.sqrt(
            (color1.r - color2.r)**2 + 
            (color1.g - color2.g)**2 + 
            (color1.b - color2.b)**2
        )
        
        # Normalize distance (maximum distance is sqrt(3 * 255^2))
        max_distance = np.sqrt(3 * 255**2)
        normalized_distance = distance / max_distance
        
        return normalized_distance < threshold
