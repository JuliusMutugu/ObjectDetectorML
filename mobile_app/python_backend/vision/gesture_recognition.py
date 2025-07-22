"""
Gesture recognition module for hand gestures.
"""
import math
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GestureRecognizer:
    """Advanced gesture recognition from hand landmarks."""
    
    def __init__(self):
        """Initialize gesture recognizer."""
        self.is_initialized = False
        self.gesture_history = []
        self.history_size = 5
        
    async def initialize(self):
        """Initialize the gesture recognizer."""
        self.is_initialized = True
        logger.info("Advanced gesture recognizer initialized")
    
    async def recognize(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Recognize gesture from hand landmarks with temporal smoothing.
        
        Args:
            landmarks: List of hand landmarks
            
        Returns:
            Recognized gesture information
        """
        if not self.is_initialized or len(landmarks) < 5:
            return {"name": "unknown", "confidence": 0.0}
        
        try:
            # Analyze current gesture
            current_gesture = self._analyze_gesture(landmarks)
            
            # Add to history for temporal smoothing
            self.gesture_history.append(current_gesture)
            if len(self.gesture_history) > self.history_size:
                self.gesture_history.pop(0)
            
            # Apply temporal smoothing
            smoothed_gesture = self._smooth_gestures()
            
            return smoothed_gesture
            
        except Exception as e:
            logger.error(f"Gesture recognition error: {e}")
            return {"name": "unknown", "confidence": 0.0}
    
    def _analyze_gesture(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze landmarks to determine gesture."""
        if len(landmarks) < 21:  # Basic mode
            return self._analyze_basic_gesture(landmarks)
        else:  # Full MediaPipe landmarks
            return self._analyze_advanced_gesture(landmarks)
    
    def _analyze_basic_gesture(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze gesture with basic landmarks."""
        palm = landmarks[0]
        
        # Calculate spread of points
        distances = []
        for i in range(1, len(landmarks)):
            dist = math.sqrt(
                (landmarks[i]["x"] - palm["x"]) ** 2 + 
                (landmarks[i]["y"] - palm["y"]) ** 2
            )
            distances.append(dist)
        
        avg_distance = sum(distances) / len(distances)
        
        if avg_distance > 60:
            return {"name": "open_hand", "confidence": 0.8}
        elif avg_distance < 30:
            return {"name": "fist", "confidence": 0.8}
        else:
            return {"name": "partial_close", "confidence": 0.6}
    
    def _analyze_advanced_gesture(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze gesture with full MediaPipe landmarks."""
        # Key landmark indices for MediaPipe
        THUMB_TIP = 4
        THUMB_IP = 3
        INDEX_TIP = 8
        INDEX_PIP = 6
        MIDDLE_TIP = 12
        MIDDLE_PIP = 10
        RING_TIP = 16
        RING_PIP = 14
        PINKY_TIP = 20
        PINKY_PIP = 18
        WRIST = 0
        
        # Calculate if fingers are extended
        fingers_up = self._get_fingers_up(landmarks)
        total_fingers = sum(fingers_up)
        
        # Check for specific gestures
        gesture = self._classify_gesture(fingers_up, landmarks)
        
        return gesture
    
    def _get_fingers_up(self, landmarks: List[Dict[str, float]]) -> List[int]:
        """Determine which fingers are extended."""
        fingers = []
        
        # Thumb (compare x coordinates due to thumb orientation)
        if landmarks[4]["x"] > landmarks[3]["x"]:  # Right hand
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers (compare y coordinates)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip]["y"] < landmarks[pip]["y"]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def _classify_gesture(self, fingers_up: List[int], landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Classify gesture based on finger positions."""
        total = sum(fingers_up)
        
        # Fist
        if total == 0:
            return {"name": "fist", "confidence": 0.95}
        
        # Pointing finger
        elif total == 1 and fingers_up[1] == 1:
            return {"name": "point", "confidence": 0.95}
        
        # Peace sign or Victory
        elif total == 2 and fingers_up[1] == 1 and fingers_up[2] == 1:
            return {"name": "peace", "confidence": 0.95}
        
        # OK sign (thumb and index form circle)
        elif self._is_ok_gesture(landmarks):
            return {"name": "ok", "confidence": 0.90}
        
        # Thumbs up
        elif total == 1 and fingers_up[0] == 1:
            return {"name": "thumbs_up", "confidence": 0.90}
        
        # Three fingers
        elif total == 3 and fingers_up[1:4] == [1, 1, 1]:
            return {"name": "three", "confidence": 0.90}
        
        # Four fingers
        elif total == 4 and fingers_up[1:] == [1, 1, 1, 1]:
            return {"name": "four", "confidence": 0.90}
        
        # Open hand
        elif total == 5:
            return {"name": "open_hand", "confidence": 0.95}
        
        # Rock and roll (index and pinky up)
        elif total == 2 and fingers_up[1] == 1 and fingers_up[4] == 1:
            return {"name": "rock_on", "confidence": 0.90}
        
        # Call me (thumb and pinky up)
        elif total == 2 and fingers_up[0] == 1 and fingers_up[4] == 1:
            return {"name": "call_me", "confidence": 0.90}
        
        # Default to finger count
        else:
            return {"name": f"{total}_fingers", "confidence": 0.70}
    
    def _is_ok_gesture(self, landmarks: List[Dict[str, float]]) -> bool:
        """Check if thumb and index finger form OK gesture."""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Calculate distance between thumb and index fingertips
        distance = math.sqrt(
            (thumb_tip["x"] - index_tip["x"]) ** 2 + 
            (thumb_tip["y"] - index_tip["y"]) ** 2
        )
        
        # If distance is small, they might be forming a circle
        return distance < 30
    
    def _smooth_gestures(self) -> Dict[str, Any]:
        """Apply temporal smoothing to gesture recognition."""
        if not self.gesture_history:
            return {"name": "unknown", "confidence": 0.0}
        
        # Count occurrences of each gesture
        gesture_counts = {}
        total_confidence = 0
        
        for gesture in self.gesture_history:
            name = gesture["name"]
            confidence = gesture["confidence"]
            
            if name in gesture_counts:
                gesture_counts[name]["count"] += 1
                gesture_counts[name]["total_confidence"] += confidence
            else:
                gesture_counts[name] = {"count": 1, "total_confidence": confidence}
            
            total_confidence += confidence
        
        # Find most frequent gesture
        most_frequent = max(gesture_counts.items(), key=lambda x: x[1]["count"])
        gesture_name = most_frequent[0]
        gesture_data = most_frequent[1]
        
        # Calculate smoothed confidence
        smoothed_confidence = gesture_data["total_confidence"] / gesture_data["count"]
        
        # Boost confidence if gesture is consistent
        consistency_boost = gesture_data["count"] / len(self.gesture_history)
        final_confidence = min(smoothed_confidence * (1 + consistency_boost * 0.3), 1.0)
        
        return {
            "name": gesture_name,
            "confidence": final_confidence,
            "consistency": consistency_boost
        }
