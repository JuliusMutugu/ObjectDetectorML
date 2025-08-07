"""
Visual Navigation Assistant for Blind and Visually Impaired Users
This module provides audio feedback and navigation assistance using object detection.
"""
import cv2
import numpy as np
import time
import threading
from typing import List, Dict, Optional, Tuple
from main import ObjectDetectionApp
from models import DetectedObject, DetectionResult
import json
from datetime import datetime

# Text-to-Speech imports
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 not available. Install with: pip install pyttsx3")

# Audio feedback imports
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  pygame not available. Install with: pip install pygame")


class NavigationAssistant:
    """
    Navigation assistant for blind and visually impaired users.
    Provides audio feedback about detected objects and their locations.
    """
    
    def __init__(self):
        """Initialize the navigation assistant."""
        # Initialize text-to-speech
        self.tts_engine = None
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self._configure_tts()
        
        # Initialize audio system
        if AUDIO_AVAILABLE:
            pygame.mixer.init()
        
        # Navigation state
        self.last_announcement_time = {}
        self.announcement_cooldown = 3.0  # Seconds between same object announcements
        self.is_speaking = False
        self.speech_queue = []
        
        # Object tracking
        self.tracked_objects = {}
        self.object_history = []
        
        # Safety zones (divide frame into regions)
        self.frame_width = 640
        self.frame_height = 480
        self.zones = self._define_safety_zones()
        
        # Priority objects for navigation
        self.navigation_objects = {
            'obstacles': ['chair', 'table', 'person', 'car', 'bicycle'],
            'landmarks': ['door', 'window', 'stairs', 'elevator'],
            'hazards': ['hole', 'step', 'barrier', 'pole']
        }
        
        # Audio feedback settings
        self.enable_object_detection = True
        self.enable_distance_feedback = True
        self.enable_direction_feedback = True
        self.enable_collision_warning = True
        
    def _configure_tts(self):
        """Configure text-to-speech engine."""
        if self.tts_engine:
            try:
                # Set speech rate (words per minute) - slower for clarity
                self.tts_engine.setProperty('rate', 150)
                
                # Set volume (0.0 to 1.0) - louder for better hearing
                self.tts_engine.setProperty('volume', 1.0)
                
                # Try to set a clear voice
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    print(f"🔊 Available voices: {len(voices)}")
                    # List available voices for debugging
                    for i, voice in enumerate(voices[:3]):  # Show first 3 voices
                        print(f"   Voice {i}: {voice.name}")
                    
                    # Prefer female voice if available (often clearer)
                    voice_set = False
                    for voice in voices:
                        if any(keyword in voice.name.lower() for keyword in ['female', 'zira', 'hazel', 'susan']):
                            self.tts_engine.setProperty('voice', voice.id)
                            print(f"✅ Selected voice: {voice.name}")
                            voice_set = True
                            break
                    
                    if not voice_set:
                        # Use first available voice
                        self.tts_engine.setProperty('voice', voices[0].id)
                        print(f"✅ Using default voice: {voices[0].name}")
                
                # Test the TTS engine
                print("🔊 Testing TTS engine...")
                self.tts_engine.say("Navigation assistant audio test")
                self.tts_engine.runAndWait()
                print("✅ TTS test completed")
                
            except Exception as e:
                print(f"❌ TTS configuration error: {e}")
                self.tts_engine = None
    
    def _define_safety_zones(self) -> Dict[str, Dict]:
        """Define safety zones in the camera frame."""
        return {
            'immediate_left': {
                'x_range': (0, self.frame_width // 3),
                'y_range': (self.frame_height // 2, self.frame_height),
                'priority': 'high',
                'description': 'immediate left'
            },
            'immediate_center': {
                'x_range': (self.frame_width // 3, 2 * self.frame_width // 3),
                'y_range': (self.frame_height // 2, self.frame_height),
                'priority': 'critical',
                'description': 'directly ahead'
            },
            'immediate_right': {
                'x_range': (2 * self.frame_width // 3, self.frame_width),
                'y_range': (self.frame_height // 2, self.frame_height),
                'priority': 'high',
                'description': 'immediate right'
            },
            'far_left': {
                'x_range': (0, self.frame_width // 3),
                'y_range': (0, self.frame_height // 2),
                'priority': 'medium',
                'description': 'far left'
            },
            'far_center': {
                'x_range': (self.frame_width // 3, 2 * self.frame_width // 3),
                'y_range': (0, self.frame_height // 2),
                'priority': 'medium',
                'description': 'ahead in distance'
            },
            'far_right': {
                'x_range': (2 * self.frame_width // 3, self.frame_width),
                'y_range': (0, self.frame_height // 2),
                'priority': 'medium',
                'description': 'far right'
            }
        }
    
    def analyze_scene(self, detection_result: DetectionResult) -> Dict:
        """
        Analyze the scene for navigation assistance.
        
        Args:
            detection_result: Detection results from the main system
            
        Returns:
            Dict: Navigation analysis
        """
        analysis = {
            'timestamp': time.time(),
            'total_objects': len(detection_result.objects),
            'zone_analysis': {},
            'navigation_advice': [],
            'warnings': [],
            'objects_by_zone': {}
        }
        
        # Analyze objects by zone
        for zone_name, zone_config in self.zones.items():
            zone_objects = self._get_objects_in_zone(detection_result.objects, zone_config)
            analysis['objects_by_zone'][zone_name] = zone_objects
            
            if zone_objects:
                analysis['zone_analysis'][zone_name] = {
                    'object_count': len(zone_objects),
                    'priority': zone_config['priority'],
                    'objects': [(obj.color.name if obj.color else 'unknown', 
                               obj.shape.name if obj.shape else 'unknown') for obj in zone_objects]
                }
        
        # Generate navigation advice
        analysis['navigation_advice'] = self._generate_navigation_advice(analysis)
        
        # Generate warnings
        analysis['warnings'] = self._generate_warnings(analysis)
        
        return analysis
    
    def _get_objects_in_zone(self, objects: List[DetectedObject], zone_config: Dict) -> List[DetectedObject]:
        """Get objects within a specific zone."""
        zone_objects = []
        x_min, x_max = zone_config['x_range']
        y_min, y_max = zone_config['y_range']
        
        for obj in objects:
            # Check if object center is in the zone
            center_x = obj.bounding_box.x + obj.bounding_box.width // 2
            center_y = obj.bounding_box.y + obj.bounding_box.height // 2
            
            if x_min <= center_x <= x_max and y_min <= center_y <= y_max:
                zone_objects.append(obj)
        
        return zone_objects
    
    def _generate_navigation_advice(self, analysis: Dict) -> List[str]:
        """Generate navigation advice based on scene analysis."""
        advice = []
        
        # Check immediate zones first
        immediate_zones = ['immediate_left', 'immediate_center', 'immediate_right']
        for zone in immediate_zones:
            if zone in analysis['objects_by_zone'] and analysis['objects_by_zone'][zone]:
                objects = analysis['objects_by_zone'][zone]
                zone_desc = self.zones[zone]['description']
                
                if len(objects) == 1:
                    obj = objects[0]
                    color = obj.color.name if obj.color else 'unknown color'
                    shape = obj.shape.name if obj.shape else 'object'
                    advice.append(f"{color} {shape} {zone_desc}")
                else:
                    advice.append(f"{len(objects)} objects {zone_desc}")
        
        # Path guidance
        clear_zones = []
        for zone in immediate_zones:
            if zone not in analysis['objects_by_zone'] or not analysis['objects_by_zone'][zone]:
                clear_zones.append(zone.replace('immediate_', ''))
        
        if clear_zones:
            if 'center' in clear_zones:
                advice.append("Path ahead is clear")
            elif 'left' in clear_zones:
                advice.append("Move left to avoid obstacles")
            elif 'right' in clear_zones:
                advice.append("Move right to avoid obstacles")
        
        return advice
    
    def _generate_warnings(self, analysis: Dict) -> List[str]:
        """Generate safety warnings."""
        warnings = []
        
        # Critical zone warnings
        critical_objects = analysis['objects_by_zone'].get('immediate_center', [])
        if critical_objects:
            warnings.append("CAUTION: Obstacle directly ahead")
        
        # Multiple object warning
        total_immediate = sum(len(analysis['objects_by_zone'].get(zone, [])) 
                            for zone in ['immediate_left', 'immediate_center', 'immediate_right'])
        if total_immediate >= 3:
            warnings.append("Multiple obstacles detected nearby")
        
        return warnings
    
    def provide_audio_feedback(self, analysis: Dict):
        """Provide audio feedback based on analysis."""
        if not self.tts_engine:
            print("🔊 TTS not available, showing text feedback:")
            self._print_feedback(analysis)
            return
        
        # Priority: Warnings first, then advice
        messages = []
        
        # Add warnings
        for warning in analysis['warnings']:
            messages.append(warning)
        
        # Add navigation advice (limit to avoid overwhelm)
        for advice in analysis['navigation_advice'][:2]:  # Limit to 2 pieces of advice
            if not any(warning.lower() in advice.lower() for warning in analysis['warnings']):
                messages.append(advice)
        
        # Speak messages
        for message in messages:
            self._speak_message(message)
    
    def _speak_message(self, message: str):
        """Speak a message using TTS."""
        current_time = time.time()
        
        # Check cooldown to avoid spam
        if message in self.last_announcement_time:
            if current_time - self.last_announcement_time[message] < self.announcement_cooldown:
                return
        
        self.last_announcement_time[message] = current_time
        
        print(f"🔊 Speaking: {message}")  # Debug output
        
        if self.tts_engine and not self.is_speaking:
            self.is_speaking = True
            try:
                # Clear any pending speech
                self.tts_engine.stop()
                
                # Speak the message
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
                
                print(f"✅ Spoke: {message}")  # Debug confirmation
            except Exception as e:
                print(f"❌ TTS error: {e}")
                # Fallback to console output
                print(f"📢 AUDIO: {message}")
            finally:
                self.is_speaking = False
        else:
            # Fallback to console output when TTS is busy or unavailable
            print(f"📢 AUDIO: {message}")
    
    def _print_feedback(self, analysis: Dict):
        """Print feedback to console when TTS is not available."""
        print(f"\n🔊 Navigation Feedback ({analysis['total_objects']} objects detected):")
        
        for warning in analysis['warnings']:
            print(f"⚠️  WARNING: {warning}")
        
        for advice in analysis['navigation_advice']:
            print(f"🧭 {advice}")
        
        # Zone summary
        for zone, objects in analysis['objects_by_zone'].items():
            if objects:
                zone_desc = self.zones[zone]['description']
                print(f"📍 {zone_desc}: {len(objects)} object(s)")
    
    def save_navigation_log(self, analysis: Dict, filename: str = None):
        """Save navigation analysis to a log file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"navigation_log_{timestamp}.json"
        
        log_entry = {
            'timestamp': datetime.fromtimestamp(analysis['timestamp']).isoformat(),
            'analysis': analysis
        }
        
        try:
            # Try to load existing log
            try:
                with open(filename, 'r') as f:
                    log_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                log_data = {'sessions': []}
            
            # Add new entry
            log_data['sessions'].append(log_entry)
            
            # Save updated log
            with open(filename, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving navigation log: {e}")


class BlindNavigationApp(ObjectDetectionApp):
    """
    Extended object detection app for blind navigation assistance.
    """
    
    def __init__(self):
        """Initialize the blind navigation app."""
        super().__init__()
        self.navigation_assistant = NavigationAssistant()
        self.window_name = "Blind Navigation Assistant"
        
        # Override display settings for accessibility
        self.display_config.update({
            'show_zones': True,
            'show_navigation_info': True,
            'large_text': True
        })
        
        print("🎯 Blind Navigation Assistant Initialized")
        print("📋 Features:")
        print("  • Real-time object detection with audio feedback")
        print("  • Zone-based navigation assistance")
        print("  • Collision warnings")
        print("  • Path guidance")
        print("🎮 Controls:")
        print("  • Press 'q' to quit")
        print("  • Press 'v' to toggle voice feedback")
        print("  • Press 's' to save navigation log")
    
    def _process_frame(self) -> None:
        """Process frame with navigation assistance."""
        # Capture frame
        frame = self.camera.capture_frame()
        if frame is None:
            return
        
        # Update frame dimensions for navigation assistant
        self.navigation_assistant.frame_height, self.navigation_assistant.frame_width = frame.shape[:2]
        self.navigation_assistant.zones = self.navigation_assistant._define_safety_zones()
        
        # Detect objects
        detected_objects = self.detector.detect_objects(frame)
        
        # Analyze colors and shapes for each detected object
        for obj in detected_objects:
            obj.color = self.color_analyzer.analyze_color(frame, obj)
            obj.shape = self.shape_analyzer.analyze_shape(obj)
        
        # Create detection result
        detection_result = DetectionResult(
            objects=detected_objects,
            frame=frame,
            timestamp=time.time()
        )
        
        # Navigation analysis
        navigation_analysis = self.navigation_assistant.analyze_scene(detection_result)
        
        # Provide audio feedback
        self.navigation_assistant.provide_audio_feedback(navigation_analysis)
        
        # Visualize results with navigation zones
        display_frame = self._visualize_navigation_results(detection_result, navigation_analysis)
        
        # Show frame
        cv2.imshow(self.window_name, display_frame)
        
        # Update frame counter and FPS
        self._update_fps()
    
    def _visualize_navigation_results(self, detection_result: DetectionResult, 
                                    navigation_analysis: Dict) -> np.ndarray:
        """Visualize results with navigation zones and accessibility features."""
        frame = detection_result.frame.copy()
        
        # Draw navigation zones
        if self.display_config.get('show_zones', True):
            frame = self._draw_navigation_zones(frame)
        
        # Draw objects with enhanced visibility
        frame = self._draw_accessible_objects(frame, detection_result.objects)
        
        # Draw navigation information
        if self.display_config.get('show_navigation_info', True):
            frame = self._draw_navigation_info(frame, navigation_analysis)
        
        return frame
    
    def _draw_navigation_zones(self, frame: np.ndarray) -> np.ndarray:
        """Draw navigation safety zones."""
        zones = self.navigation_assistant.zones
        
        zone_colors = {
            'critical': (0, 0, 255),    # Red
            'high': (0, 165, 255),      # Orange
            'medium': (0, 255, 255)     # Yellow
        }
        
        for zone_name, zone_config in zones.items():
            x_min, x_max = zone_config['x_range']
            y_min, y_max = zone_config['y_range']
            priority = zone_config['priority']
            
            color = zone_colors.get(priority, (128, 128, 128))
            
            # Draw zone boundary
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
            
            # Draw zone label
            label = f"{zone_name.replace('_', ' ').title()}"
            cv2.putText(frame, label, (x_min + 5, y_min + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return frame
    
    def _draw_accessible_objects(self, frame: np.ndarray, objects: List[DetectedObject]) -> np.ndarray:
        """Draw objects with high contrast for accessibility."""
        for obj in objects:
            # Draw thick, high-contrast bounding box
            bbox = obj.bounding_box
            cv2.rectangle(frame, 
                         (bbox.x, bbox.y), 
                         (bbox.x + bbox.width, bbox.y + bbox.height),
                         (0, 255, 0), 4)  # Thick green border
            
            # Draw filled background for text
            if obj.color and obj.shape:
                text = f"{obj.color.name} {obj.shape.name}"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                
                # Black background for text
                cv2.rectangle(frame,
                             (bbox.x, bbox.y - text_size[1] - 10),
                             (bbox.x + text_size[0] + 10, bbox.y),
                             (0, 0, 0), -1)
                
                # White text for maximum contrast
                cv2.putText(frame, text, (bbox.x + 5, bbox.y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return frame
    
    def _draw_navigation_info(self, frame: np.ndarray, analysis: Dict) -> np.ndarray:
        """Draw navigation information on frame."""
        y_offset = 30
        
        # Object count
        count_text = f"Objects: {analysis['total_objects']}"
        cv2.putText(frame, count_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        y_offset += 40
        
        # Warnings
        for warning in analysis['warnings']:
            cv2.putText(frame, f"WARNING: {warning}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            y_offset += 30
        
        # Navigation advice
        for advice in analysis['navigation_advice'][:3]:  # Show max 3 lines
            cv2.putText(frame, advice, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 25
        
        return frame
    
    def run(self) -> None:
        """Run the navigation assistant."""
        try:
            if not self._initialize():
                print("Failed to initialize navigation assistant")
                return
            
            print("🎯 Blind Navigation Assistant started!")
            print("🔊 Audio feedback enabled" if self.navigation_assistant.tts_engine else "📝 Text feedback mode")
            self.is_running = True
            
            while self.is_running:
                self._process_frame()
                
                # Check for quit command and additional controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC key
                    break
                elif key == ord('v'):  # Toggle voice
                    self._toggle_voice_feedback()
                elif key == ord('s'):  # Save log
                    self._save_current_log()
                    
        except KeyboardInterrupt:
            print("\nNavigation assistant interrupted by user")
        except Exception as e:
            print(f"Navigation assistant error: {e}")
        finally:
            self._cleanup()
    
    def _toggle_voice_feedback(self):
        """Toggle voice feedback on/off."""
        if self.navigation_assistant.tts_engine:
            self.navigation_assistant.enable_object_detection = not self.navigation_assistant.enable_object_detection
            status = "enabled" if self.navigation_assistant.enable_object_detection else "disabled"
            print(f"🔊 Voice feedback {status}")
        else:
            print("🔊 TTS not available")
    
    def _save_current_log(self):
        """Save current navigation session log."""
        print("💾 Saving navigation log...")
        # This would save the current session - implementation depends on requirements


def main():
    """Main entry point for the blind navigation assistant."""
    print("🎯 Blind Navigation Assistant")
    print("=" * 50)
    print("Assistive technology for blind and visually impaired users")
    print("Provides real-time audio feedback about objects and navigation")
    print()
    
    # Check dependencies
    if not TTS_AVAILABLE:
        print("⚠️  Installing text-to-speech...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "pyttsx3"])
            print("✅ Text-to-speech installed successfully")
        except:
            print("❌ Failed to install TTS. Audio feedback will be limited.")
    
    app = BlindNavigationApp()
    app.run()


if __name__ == "__main__":
    main()
