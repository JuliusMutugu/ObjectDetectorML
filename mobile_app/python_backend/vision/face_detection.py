"""
Face detection using MediaPipe.
"""
import cv2
import numpy as np
from typing import List, Dict, Any
import asyncio
import logging

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logging.warning("MediaPipe not available. Face detection will use OpenCV cascade.")

logger = logging.getLogger(__name__)


class FaceDetector:
    """Face detection using MediaPipe or OpenCV."""
    
    def __init__(self):
        """Initialize face detector."""
        self.is_initialized = False
        self.use_mediapipe = MEDIAPIPE_AVAILABLE
        
        if self.use_mediapipe:
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_drawing = mp.solutions.drawing_utils
            self.face_detection = None
        else:
            # Fallback to OpenCV Haar cascade
            self.face_cascade = None
    
    async def initialize(self):
        """Initialize the face detector."""
        try:
            if self.use_mediapipe:
                self.face_detection = self.mp_face_detection.FaceDetection(
                    model_selection=0, min_detection_confidence=0.5
                )
                logger.info("MediaPipe face detector initialized")
            else:
                # Try to load OpenCV cascade (might not be available in all installations)
                try:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    logger.info("OpenCV face cascade initialized")
                except Exception as e:
                    logger.warning(f"OpenCV cascade not available: {e}")
                    # Create a simple face detector placeholder
                    self.face_cascade = None
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize face detector: {e}")
            self.is_initialized = False
    
    async def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detected faces with landmarks
        """
        if not self.is_initialized:
            return []
        
        try:
            if self.use_mediapipe and self.face_detection:
                return await self._detect_with_mediapipe(image)
            elif self.face_cascade is not None:
                return await self._detect_with_opencv(image)
            else:
                # Fallback: simple mock detection for demonstration
                return await self._detect_mock(image)
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []
    
    async def _detect_with_mediapipe(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces using MediaPipe."""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        faces = []
        if results.detections:
            for i, detection in enumerate(results.detections):
                bbox = detection.location_data.relative_bounding_box
                h, w = image.shape[:2]
                
                # Convert relative coordinates to absolute
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Get landmarks if available
                landmarks = []
                if hasattr(detection.location_data, 'relative_keypoints'):
                    for landmark in detection.location_data.relative_keypoints:
                        landmarks.append({
                            "x": landmark.x * w,
                            "y": landmark.y * h
                        })
                
                face_data = {
                    "id": i,
                    "bbox": {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    },
                    "confidence": detection.score[0],
                    "landmarks": landmarks
                }
                faces.append(face_data)
        
        return faces
    
    async def _detect_with_opencv(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces using OpenCV cascade."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces_rects = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        faces = []
        for i, (x, y, w, h) in enumerate(faces_rects):
            face_data = {
                "id": i,
                "bbox": {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h)
                },
                "confidence": 0.8,  # OpenCV doesn't provide confidence
                "landmarks": []  # Basic cascade doesn't provide landmarks
            }
            faces.append(face_data)
        
        return faces
    
    async def _detect_mock(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Mock face detection for demonstration when no detector is available."""
        # Simple color-based face detection (skin tone detection)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        faces = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum face area
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (faces are roughly rectangular)
                aspect_ratio = w / h
                if 0.7 <= aspect_ratio <= 1.3:
                    face_data = {
                        "id": i,
                        "bbox": {
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h)
                        },
                        "confidence": 0.6,
                        "landmarks": [],
                        "method": "skin_detection"
                    }
                    faces.append(face_data)
        
        return faces[:3]  # Limit to 3 faces
