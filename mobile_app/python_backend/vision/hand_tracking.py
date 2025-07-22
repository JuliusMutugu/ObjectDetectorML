"""
Hand tracking and gesture recognition using MediaPipe.
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import asyncio
import logging
import math

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logging.warning("MediaPipe not available. Hand tracking will use basic detection.")

logger = logging.getLogger(__name__)


class HandTracker:
    """Hand tracking using MediaPipe or basic detection."""
    
    def __init__(self):
        """Initialize hand tracker."""
        self.is_initialized = False
        self.use_mediapipe = MEDIAPIPE_AVAILABLE
        
        if self.use_mediapipe:
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands = None
        
    async def initialize(self):
        """Initialize the hand tracker."""
        try:
            if self.use_mediapipe:
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                logger.info("MediaPipe hand tracker initialized")
            else:
                logger.info("Basic hand tracker initialized")
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize hand tracker: {e}")
            self.is_initialized = False
    
    async def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect hands in image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detected hands with landmarks
        """
        if not self.is_initialized:
            return []
        
        try:
            if self.use_mediapipe and self.hands:
                return await self._detect_with_mediapipe(image)
            else:
                return await self._detect_basic(image)
            
        except Exception as e:
            logger.error(f"Hand detection error: {e}")
            return []
    
    async def _detect_with_mediapipe(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect hands using MediaPipe."""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_image)
        
        hands = []
        if results.multi_hand_landmarks:
            h, w = image.shape[:2]
            
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Extract landmarks
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        "x": landmark.x * w,
                        "y": landmark.y * h,
                        "z": landmark.z
                    })
                
                # Calculate bounding box
                x_coords = [lm["x"] for lm in landmarks]
                y_coords = [lm["y"] for lm in landmarks]
                
                bbox = {
                    "x": int(min(x_coords)),
                    "y": int(min(y_coords)),
                    "width": int(max(x_coords) - min(x_coords)),
                    "height": int(max(y_coords) - min(y_coords))
                }
                
                # Get hand classification if available
                handedness = "Unknown"
                if results.multi_handedness:
                    if i < len(results.multi_handedness):
                        handedness = results.multi_handedness[i].classification[0].label
                
                hand_data = {
                    "id": i,
                    "handedness": handedness,
                    "bbox": bbox,
                    "landmarks": landmarks,
                    "confidence": 0.8
                }
                hands.append(hand_data)
        
        return hands
    
    async def _detect_basic(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Basic hand detection using skin color."""
        # Convert to HSV for skin detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define skin color range
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hands = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 2000:  # Minimum hand area
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (hands are roughly square-ish)
                aspect_ratio = w / h
                if 0.5 <= aspect_ratio <= 2.0:
                    # Generate basic landmarks (just 5 points)
                    landmarks = self._generate_basic_landmarks(contour, x, y, w, h)
                    
                    hand_data = {
                        "id": i,
                        "handedness": "Unknown",
                        "bbox": {
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h)
                        },
                        "landmarks": landmarks,
                        "confidence": 0.6,
                        "method": "skin_detection"
                    }
                    hands.append(hand_data)
        
        return hands[:2]  # Limit to 2 hands
    
    def _generate_basic_landmarks(self, contour: np.ndarray, x: int, y: int, w: int, h: int) -> List[Dict[str, float]]:
        """Generate basic hand landmarks from contour."""
        # Find convex hull and defects
        hull = cv2.convexHull(contour, returnPoints=False)
        
        if len(hull) > 3:
            defects = cv2.convexityDefects(contour, hull)
            
            landmarks = []
            
            # Add center point (palm)
            landmarks.append({
                "x": float(x + w // 2),
                "y": float(y + h // 2),
                "z": 0.0
            })
            
            # Add corner points as finger tips
            landmarks.append({"x": float(x), "y": float(y), "z": 0.0})  # Top-left
            landmarks.append({"x": float(x + w), "y": float(y), "z": 0.0})  # Top-right
            landmarks.append({"x": float(x), "y": float(y + h), "z": 0.0})  # Bottom-left
            landmarks.append({"x": float(x + w), "y": float(y + h), "z": 0.0})  # Bottom-right
            
            return landmarks
        
        # Fallback: just return corner points
        return [
            {"x": float(x + w // 2), "y": float(y + h // 2), "z": 0.0},
            {"x": float(x), "y": float(y), "z": 0.0},
            {"x": float(x + w), "y": float(y), "z": 0.0},
            {"x": float(x), "y": float(y + h), "z": 0.0},
            {"x": float(x + w), "y": float(y + h), "z": 0.0}
        ]


class GestureRecognizer:
    """Gesture recognition based on hand landmarks."""
    
    def __init__(self):
        """Initialize gesture recognizer."""
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the gesture recognizer."""
        self.is_initialized = True
        logger.info("Gesture recognizer initialized")
    
    async def recognize(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Recognize gesture from hand landmarks.
        
        Args:
            landmarks: List of hand landmarks
            
        Returns:
            Recognized gesture information
        """
        if not self.is_initialized or len(landmarks) < 5:
            return {"name": "unknown", "confidence": 0.0}
        
        try:
            # Basic gesture recognition
            gesture = self._analyze_gesture(landmarks)
            return gesture
            
        except Exception as e:
            logger.error(f"Gesture recognition error: {e}")
            return {"name": "unknown", "confidence": 0.0}
    
    def _analyze_gesture(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze landmarks to determine gesture."""
        if len(landmarks) < 21:  # Basic mode
            return self._analyze_basic_gesture(landmarks)
        else:  # Full MediaPipe landmarks
            return self._analyze_full_gesture(landmarks)
    
    def _analyze_basic_gesture(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze gesture with basic landmarks."""
        # For basic detection, we can only determine simple gestures
        palm = landmarks[0]
        
        # Calculate spread of points (open vs closed hand)
        distances = []
        for i in range(1, len(landmarks)):
            dist = math.sqrt(
                (landmarks[i]["x"] - palm["x"]) ** 2 + 
                (landmarks[i]["y"] - palm["y"]) ** 2
            )
            distances.append(dist)
        
        avg_distance = sum(distances) / len(distances)
        
        if avg_distance > 50:
            return {"name": "open_hand", "confidence": 0.7}
        else:
            return {"name": "closed_hand", "confidence": 0.7}
    
    def _analyze_full_gesture(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze gesture with full MediaPipe landmarks."""
        # Implement gesture recognition using MediaPipe landmark positions
        # This is a simplified version - you can expand with more gestures
        
        # Get key landmarks
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        wrist = landmarks[0]
        
        # Calculate if fingers are extended
        fingers_up = []
        
        # Thumb
        if thumb_tip["x"] > landmarks[3]["x"]:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        # Other fingers
        for tip_id in [8, 12, 16, 20]:
            if landmarks[tip_id]["y"] < landmarks[tip_id - 2]["y"]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        total_fingers = sum(fingers_up)
        
        # Recognize gestures based on finger count
        if total_fingers == 0:
            return {"name": "fist", "confidence": 0.9}
        elif total_fingers == 1 and fingers_up[1] == 1:
            return {"name": "point", "confidence": 0.9}
        elif total_fingers == 2 and fingers_up[1] == 1 and fingers_up[2] == 1:
            return {"name": "peace", "confidence": 0.9}
        elif total_fingers == 5:
            return {"name": "open_hand", "confidence": 0.9}
        elif total_fingers == 3 and fingers_up[1:4] == [1, 1, 1]:
            return {"name": "three", "confidence": 0.9}
        elif total_fingers == 4 and fingers_up[1:] == [1, 1, 1, 1]:
            return {"name": "four", "confidence": 0.9}
        else:
            return {"name": f"{total_fingers}_fingers", "confidence": 0.7}
