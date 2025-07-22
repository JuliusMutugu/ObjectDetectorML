"""
FastAPI backend for mobile vision app.
Provides REST and WebSocket endpoints for computer vision tasks.
"""
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
import json
from typing import List, Dict, Any
import asyncio
import logging

# Import our vision modules
from vision.object_detection import ObjectDetector
from vision.face_detection import FaceDetector
from vision.hand_tracking import HandTracker
from vision.gesture_recognition import GestureRecognizer
from models.response_models import DetectionResponse, FaceResponse, HandResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vision AI Mobile Backend",
    description="Computer vision backend for mobile app with object detection, face tracking, and hand gestures",
    version="1.0.0"
)

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vision processors
object_detector = ObjectDetector()
face_detector = FaceDetector()
hand_tracker = HandTracker()
gesture_recognizer = GestureRecognizer()


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    logger.info("Loading computer vision models...")
    await object_detector.initialize()
    await face_detector.initialize()
    await hand_tracker.initialize()
    await gesture_recognizer.initialize()
    logger.info("All models loaded successfully!")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Vision AI Mobile Backend is running!"}


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "models_loaded": {
            "object_detector": object_detector.is_initialized,
            "face_detector": face_detector.is_initialized,
            "hand_tracker": hand_tracker.is_initialized,
            "gesture_recognizer": gesture_recognizer.is_initialized
        }
    }


# Object Detection Endpoints
@app.post("/api/detect/objects", response_model=DetectionResponse)
async def detect_objects(file: UploadFile = File(...)):
    """Detect objects in uploaded image."""
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect objects
        results = await object_detector.detect(image)
        
        return DetectionResponse(
            success=True,
            objects=results,
            message=f"Detected {len(results)} objects"
        )
    
    except Exception as e:
        logger.error(f"Object detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect/objects/base64")
async def detect_objects_base64(data: Dict[str, str]):
    """Detect objects in base64 encoded image."""
    try:
        # Decode base64 image
        image_data = base64.b64decode(data["image"])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect objects
        results = await object_detector.detect(image)
        
        return {
            "success": True,
            "objects": results,
            "message": f"Detected {len(results)} objects"
        }
    
    except Exception as e:
        logger.error(f"Object detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Face Detection Endpoints
@app.post("/api/detect/faces", response_model=FaceResponse)
async def detect_faces(file: UploadFile = File(...)):
    """Detect faces in uploaded image."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect faces
        results = await face_detector.detect(image)
        
        return FaceResponse(
            success=True,
            faces=results,
            message=f"Detected {len(results)} faces"
        )
    
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Hand Tracking Endpoints
@app.post("/api/detect/hands", response_model=HandResponse)
async def detect_hands(file: UploadFile = File(...)):
    """Detect hands and gestures in uploaded image."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect hands
        hand_results = await hand_tracker.detect(image)
        
        # Recognize gestures
        gestures = []
        for hand in hand_results:
            gesture = await gesture_recognizer.recognize(hand["landmarks"])
            gestures.append(gesture)
        
        return HandResponse(
            success=True,
            hands=hand_results,
            gestures=gestures,
            message=f"Detected {len(hand_results)} hands"
        )
    
    except Exception as e:
        logger.error(f"Hand detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoints for real-time processing
@app.websocket("/ws/objects")
async def websocket_objects(websocket: WebSocket):
    """Real-time object detection via WebSocket."""
    await websocket.accept()
    
    try:
        while True:
            # Receive image data
            data = await websocket.receive_text()
            image_data = json.loads(data)
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data["image"])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                # Detect objects
                results = await object_detector.detect(image)
                
                # Send results back
                response = {
                    "type": "objects",
                    "data": results,
                    "timestamp": image_data.get("timestamp")
                }
                await websocket.send_text(json.dumps(response))
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@app.websocket("/ws/hands")
async def websocket_hands(websocket: WebSocket):
    """Real-time hand tracking via WebSocket."""
    await websocket.accept()
    
    try:
        while True:
            # Receive image data
            data = await websocket.receive_text()
            image_data = json.loads(data)
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data["image"])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                # Detect hands
                hand_results = await hand_tracker.detect(image)
                
                # Recognize gestures
                gestures = []
                for hand in hand_results:
                    gesture = await gesture_recognizer.recognize(hand["landmarks"])
                    gestures.append(gesture)
                
                # Send results back
                response = {
                    "type": "hands",
                    "data": {
                        "hands": hand_results,
                        "gestures": gestures
                    },
                    "timestamp": image_data.get("timestamp")
                }
                await websocket.send_text(json.dumps(response))
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@app.websocket("/ws/faces")
async def websocket_faces(websocket: WebSocket):
    """Real-time face detection via WebSocket."""
    await websocket.accept()
    
    try:
        while True:
            # Receive image data
            data = await websocket.receive_text()
            image_data = json.loads(data)
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data["image"])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                # Detect faces
                results = await face_detector.detect(image)
                
                # Send results back
                response = {
                    "type": "faces",
                    "data": results,
                    "timestamp": image_data.get("timestamp")
                }
                await websocket.send_text(json.dumps(response))
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# Configuration endpoints
@app.get("/api/config/object_detection")
async def get_object_detection_config():
    """Get object detection configuration."""
    return object_detector.get_config()


@app.post("/api/config/object_detection")
async def update_object_detection_config(config: Dict[str, Any]):
    """Update object detection configuration."""
    object_detector.update_config(config)
    return {"success": True, "message": "Configuration updated"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
