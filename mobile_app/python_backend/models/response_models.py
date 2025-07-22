"""
Response models for the mobile vision API.
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x: int
    y: int
    width: int
    height: int


class Point(BaseModel):
    """2D or 3D point."""
    x: float
    y: float
    z: Optional[float] = None


class ColorInfo(BaseModel):
    """Color information."""
    name: str
    confidence: float
    rgb: List[int]


class DetectedObject(BaseModel):
    """Detected object information."""
    id: int
    bbox: BoundingBox
    center: Point
    area: int
    color: ColorInfo
    confidence: float


class DetectionResponse(BaseModel):
    """Object detection response."""
    success: bool
    objects: List[DetectedObject]
    message: str


class Face(BaseModel):
    """Detected face information."""
    id: int
    bbox: BoundingBox
    confidence: float
    landmarks: List[Point]


class FaceResponse(BaseModel):
    """Face detection response."""
    success: bool
    faces: List[Face]
    message: str


class Hand(BaseModel):
    """Detected hand information."""
    id: int
    handedness: str
    bbox: BoundingBox
    landmarks: List[Point]
    confidence: float


class Gesture(BaseModel):
    """Recognized gesture information."""
    name: str
    confidence: float
    consistency: Optional[float] = None


class HandResponse(BaseModel):
    """Hand detection response."""
    success: bool
    hands: List[Hand]
    gestures: List[Gesture]
    message: str


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str
    data: Dict[str, Any]
    timestamp: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    message: str
