"""
Advanced object detection using YOLO and our existing modular system.
"""
import cv2
import numpy as np
from typing import List, Dict, Any
import asyncio
import logging

# Import our existing object detection system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from detection import ContourDetector
from color import HSVColorAnalyzer
from models import DetectedObject, Color

logger = logging.getLogger(__name__)


class ObjectDetector:
    """Enhanced object detector for mobile app."""
    
    def __init__(self):
        """Initialize the object detector."""
        self.contour_detector = ContourDetector(
            min_contour_area=300,
            max_contour_area=100000,
            blur_kernel_size=3,
            morph_kernel_size=3
        )
        self.color_analyzer = HSVColorAnalyzer()
        self.is_initialized = False
        
        # Performance settings
        self.max_objects = 10
        self.confidence_threshold = 0.3
        
    async def initialize(self):
        """Initialize the detector."""
        try:
            # Test detection on a dummy image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            await self.detect(test_image)
            self.is_initialized = True
            logger.info("Object detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize object detector: {e}")
            self.is_initialized = False
    
    async def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect objects in image and return results.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detected objects with properties
        """
        try:
            # Resize image for better performance on mobile
            height, width = image.shape[:2]
            if width > 640:
                scale = 640 / width
                new_width = 640
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Detect objects using our contour detector
            detected_objects = self.contour_detector.detect_objects(image)
            
            # Analyze colors for each object
            results = []
            for i, obj in enumerate(detected_objects[:self.max_objects]):
                # Analyze color
                color = self.color_analyzer.analyze_color(image, obj)
                
                # Only include objects with sufficient confidence
                if color.confidence >= self.confidence_threshold:
                    result = {
                        "id": i,
                        "bbox": {
                            "x": obj.bounding_box.x,
                            "y": obj.bounding_box.y,
                            "width": obj.bounding_box.width,
                            "height": obj.bounding_box.height
                        },
                        "center": {
                            "x": obj.center.x,
                            "y": obj.center.y
                        },
                        "area": obj.area,
                        "color": {
                            "name": color.name,
                            "confidence": color.confidence,
                            "rgb": [color.r, color.g, color.b]
                        },
                        "confidence": obj.confidence
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Object detection error: {e}")
            return []
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "max_objects": self.max_objects,
            "confidence_threshold": self.confidence_threshold,
            "detector_params": self.contour_detector.get_parameters(),
            "supported_colors": self.color_analyzer.get_supported_colors()
        }
    
    def update_config(self, config: Dict[str, Any]):
        """Update configuration."""
        if "max_objects" in config:
            self.max_objects = config["max_objects"]
        if "confidence_threshold" in config:
            self.confidence_threshold = config["confidence_threshold"]
        if "detector_params" in config:
            self.contour_detector.set_parameters(**config["detector_params"])
