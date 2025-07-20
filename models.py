"""
Core data models for the object detection system.
"""
from dataclasses import dataclass
from typing import Tuple, List, Optional
import numpy as np


@dataclass
class Point:
    """Represents a 2D point."""
    x: float
    y: float


@dataclass
class BoundingBox:
    """Represents a bounding box for detected objects."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Point:
        """Get the center point of the bounding box."""
        return Point(self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def area(self) -> int:
        """Get the area of the bounding box."""
        return self.width * self.height


@dataclass
class Color:
    """Represents a color with RGB values and name."""
    r: int
    g: int
    b: int
    name: str
    confidence: float = 1.0
    
    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple."""
        return (self.r, self.g, self.b)
    
    def to_bgr_tuple(self) -> Tuple[int, int, int]:
        """Convert to BGR tuple (for OpenCV)."""
        return (self.b, self.g, self.r)


@dataclass
class DetectedObject:
    """Represents a detected object with its properties."""
    bounding_box: BoundingBox
    contour: np.ndarray
    color: Optional[Color] = None
    confidence: float = 1.0
    object_id: Optional[int] = None
    
    @property
    def center(self) -> Point:
        """Get the center point of the object."""
        return self.bounding_box.center
    
    @property
    def area(self) -> int:
        """Get the area of the object."""
        return self.bounding_box.area


@dataclass
class DetectionResult:
    """Container for detection results."""
    objects: List[DetectedObject]
    frame: np.ndarray
    timestamp: float
    
    def __len__(self) -> int:
        """Get the number of detected objects."""
        return len(self.objects)
    
    def get_objects_by_color(self, color_name: str) -> List[DetectedObject]:
        """Get objects with a specific color."""
        return [obj for obj in self.objects 
                if obj.color and obj.color.name.lower() == color_name.lower()]
