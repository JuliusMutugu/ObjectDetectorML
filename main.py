"""
Object detection application orchestrator.
This module follows the Single Responsibility Principle by focusing
on orchestrating the entire object detection pipeline.
"""
import cv2
import numpy as np
import time
from typing import List, Optional
from camera import CameraInterface, OpenCVCamera
from detection import DetectorInterface, ContourDetector
from color import ColorAnalyzerInterface, HSVColorAnalyzer
from models import DetectedObject, DetectionResult
from config import ConfigManager


class ObjectDetectionApp:
    """
    Main application class that orchestrates the object detection pipeline.
    
    This class follows the Dependency Inversion Principle by depending on
    abstractions rather than concrete implementations.
    """
    
    def __init__(self, 
                 camera: Optional[CameraInterface] = None,
                 detector: Optional[DetectorInterface] = None,
                 color_analyzer: Optional[ColorAnalyzerInterface] = None,
                 config_manager: Optional[ConfigManager] = None):
        """
        Initialize the object detection application.
        
        Args:
            camera: Camera interface implementation
            detector: Object detector implementation
            color_analyzer: Color analyzer implementation
            config_manager: Configuration manager
        """
        # Initialize configuration manager
        self.config_manager = config_manager or ConfigManager()
        
        # Load configurations
        self.detection_config = self.config_manager.get_detection_config()
        self.color_config = self.config_manager.get_color_config()
        
        # Initialize components with dependency injection
        self.camera = camera or self._create_default_camera()
        self.detector = detector or self._create_default_detector()
        self.color_analyzer = color_analyzer or self._create_default_color_analyzer()
        
        # Application state
        self.is_running = False
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Display settings
        self.display_config = self.detection_config.get('display', {})
        self.window_name = self.display_config.get('window_name', 'Object Color Detector')
    
    def run(self) -> None:
        """
        Run the main application loop.
        """
        try:
            if not self._initialize():
                print("Failed to initialize application")
                return
            
            print("Object Color Detector started. Press 'q' to quit.")
            self.is_running = True
            
            while self.is_running:
                self._process_frame()
                
                # Check for quit command
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC key
                    break
                    
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            self._cleanup()
    
    def _initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        # Initialize camera
        if not self.camera.initialize():
            print("Failed to initialize camera")
            return False
        
        # Configure detector parameters
        detector_config = self.detection_config.get('detection', {}).get('contour', {})
        self.detector.set_parameters(**detector_config)
        
        # Create OpenCV window
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        
        return True
    
    def _process_frame(self) -> None:
        """Process a single frame from the camera."""
        # Capture frame
        frame = self.camera.capture_frame()
        if frame is None:
            return
        
        # Detect objects
        detected_objects = self.detector.detect_objects(frame)
        
        # Analyze colors for each detected object
        for obj in detected_objects:
            obj.color = self.color_analyzer.analyze_color(frame, obj)
        
        # Create detection result
        detection_result = DetectionResult(
            objects=detected_objects,
            frame=frame,
            timestamp=time.time()
        )
        
        # Visualize results
        display_frame = self._visualize_results(detection_result)
        
        # Show frame
        cv2.imshow(self.window_name, display_frame)
        
        # Update frame counter and FPS
        self._update_fps()
    
    def _visualize_results(self, detection_result: DetectionResult) -> np.ndarray:
        """
        Visualize detection results on the frame.
        
        Args:
            detection_result: Detection results to visualize
            
        Returns:
            np.ndarray: Frame with visualizations
        """
        frame = detection_result.frame.copy()
        
        # Get display settings
        show_contours = self.display_config.get('show_contours', True)
        show_bboxes = self.display_config.get('show_bounding_boxes', True)
        show_labels = self.display_config.get('show_color_labels', True)
        font_scale = self.display_config.get('font_scale', 0.7)
        thickness = self.display_config.get('line_thickness', 2)
        
        for obj in detection_result.objects:
            # Draw contours
            if show_contours:
                cv2.drawContours(frame, [obj.contour], -1, (0, 255, 0), thickness)
            
            # Draw bounding box
            if show_bboxes:
                bbox = obj.bounding_box
                cv2.rectangle(frame, 
                            (bbox.x, bbox.y), 
                            (bbox.x + bbox.width, bbox.y + bbox.height),
                            (255, 0, 0), thickness)
            
            # Draw color label
            if show_labels and obj.color:
                label = f"{obj.color.name} ({obj.color.confidence:.2f})"
                label_pos = (obj.bounding_box.x, obj.bounding_box.y - 10)
                
                # Draw text background
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                cv2.rectangle(frame,
                            (label_pos[0], label_pos[1] - text_size[1] - 5),
                            (label_pos[0] + text_size[0], label_pos[1] + 5),
                            (0, 0, 0), -1)
                
                # Draw text
                cv2.putText(frame, label, label_pos,
                          cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        
        # Draw statistics
        self._draw_statistics(frame, detection_result)
        
        return frame
    
    def _draw_statistics(self, frame: np.ndarray, detection_result: DetectionResult) -> None:
        """
        Draw statistics on the frame.
        
        Args:
            frame: Frame to draw on
            detection_result: Detection results
        """
        # Statistics
        stats = [
            f"Objects: {len(detection_result.objects)}",
            f"FPS: {self.fps_counter:.1f}",
            f"Frame: {self.frame_count}"
        ]
        
        # Draw statistics
        y_offset = 30
        for stat in stats:
            cv2.putText(frame, stat, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_offset += 25
    
    def _update_fps(self) -> None:
        """Update FPS counter."""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps_counter = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        self.is_running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("Application cleanup completed")
    
    def _create_default_camera(self) -> CameraInterface:
        """Create default camera implementation."""
        camera_config = self.detection_config.get('camera', {})
        return OpenCVCamera(
            camera_index=camera_config.get('index', 0),
            width=camera_config.get('width', 640),
            height=camera_config.get('height', 480)
        )
    
    def _create_default_detector(self) -> DetectorInterface:
        """Create default detector implementation."""
        contour_config = self.detection_config.get('detection', {}).get('contour', {})
        return ContourDetector(
            min_contour_area=contour_config.get('min_area', 500),
            max_contour_area=contour_config.get('max_area', 50000),
            blur_kernel_size=contour_config.get('blur_kernel_size', 5),
            morph_kernel_size=contour_config.get('morph_kernel_size', 5)
        )
    
    def _create_default_color_analyzer(self) -> ColorAnalyzerInterface:
        """Create default color analyzer implementation."""
        return HSVColorAnalyzer()


def main():
    """Main entry point for the application."""
    app = ObjectDetectionApp()
    app.run()


if __name__ == "__main__":
    main()
