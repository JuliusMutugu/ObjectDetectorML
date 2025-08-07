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
        self.announcement_cooldown = 2.5  # Reduced cooldown for better responsiveness
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
        """Configure text-to-speech engine for optimal real-time performance."""
        if self.tts_engine:
            try:
                # Set speech rate (words per minute) - optimal for navigation
                self.tts_engine.setProperty('rate', 170)  # Slightly faster for real-time
                
                # Set volume (0.0 to 1.0) - maximum for better hearing
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
                
                # Test the TTS engine with a quick test
                print("🔊 Testing TTS engine...")
                self.tts_engine.say("Navigation assistant audio test")
                self.tts_engine.runAndWait()
                print("✅ TTS test completed")
                
                # Set up TTS engine for real-time use
                print("🎙️ TTS configured for real-time navigation")
                
            except Exception as e:
                print(f"❌ TTS configuration error: {e}")
                self.tts_engine = None
    
    def _define_safety_zones(self) -> Dict[str, Dict]:
        """Define enhanced safety zones in the camera frame - 5x3 grid for better accuracy."""
        zones = {}
        
        # Define grid dimensions (5 columns x 3 rows for better precision)
        cols = 5
        rows = 3
        col_width = self.frame_width // cols
        row_height = self.frame_height // rows
        
        # Zone naming and priorities
        row_names = ['far', 'mid', 'immediate']
        col_names = ['far_left', 'left', 'center', 'right', 'far_right']
        
        # Priority mapping based on distance and position
        priority_map = {
            'immediate_center': 'critical',      # Directly ahead and close
            'immediate_left': 'high',            # Close left
            'immediate_right': 'high',           # Close right  
            'mid_center': 'high',                # Ahead at medium distance
            'immediate_far_left': 'medium',      # Close far left
            'immediate_far_right': 'medium',     # Close far right
            'mid_left': 'medium',                # Medium distance left
            'mid_right': 'medium',               # Medium distance right
            'mid_far_left': 'low',               # Medium distance far left
            'mid_far_right': 'low',              # Medium distance far right
            'far_center': 'medium',              # Far ahead
            'far_left': 'low',                   # Far left
            'far_right': 'low',                  # Far right
            'far_far_left': 'low',               # Far far left
            'far_far_right': 'low'               # Far far right
        }
        
        # Description mapping for natural language
        description_map = {
            'immediate_center': 'directly ahead',
            'immediate_left': 'immediate left',
            'immediate_right': 'immediate right',
            'immediate_far_left': 'immediate far left',
            'immediate_far_right': 'immediate far right',
            'mid_center': 'ahead at medium distance',
            'mid_left': 'medium distance left',
            'mid_right': 'medium distance right',
            'mid_far_left': 'medium distance far left',
            'mid_far_right': 'medium distance far right',
            'far_center': 'far ahead',
            'far_left': 'far left',
            'far_right': 'far right',
            'far_far_left': 'far far left',
            'far_far_right': 'far far right'
        }
        
        # Generate all zones
        for row in range(rows):
            for col in range(cols):
                # Calculate zone boundaries
                x_start = col * col_width
                x_end = (col + 1) * col_width
                y_start = row * row_height
                y_end = (row + 1) * row_height
                
                # Create zone name
                zone_name = f"{row_names[row]}_{col_names[col]}"
                
                # Get priority and description
                priority = priority_map.get(zone_name, 'low')
                description = description_map.get(zone_name, zone_name.replace('_', ' '))
                
                zones[zone_name] = {
                    'x_range': (x_start, x_end),
                    'y_range': (y_start, y_end),
                    'priority': priority,
                    'description': description,
                    'grid_position': (row, col)  # For easier grid-based analysis
                }
        
        return zones
    
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
        """Generate enhanced navigation advice based on 5x3 grid analysis."""
        advice = []
        
        # Priority zones for immediate navigation (bottom row - closest to user)
        immediate_zones = ['immediate_far_left', 'immediate_left', 'immediate_center', 'immediate_right', 'immediate_far_right']
        
        # Check critical center zone first
        if 'immediate_center' in analysis['objects_by_zone'] and analysis['objects_by_zone']['immediate_center']:
            objects = analysis['objects_by_zone']['immediate_center']
            zone_desc = self.zones['immediate_center']['description']
            
            if len(objects) == 1:
                obj = objects[0]
                color = obj.color.name if obj.color else 'unknown color'
                shape = obj.shape.name if obj.shape else 'object'
                advice.append(f"{color} {shape} {zone_desc}")
            else:
                advice.append(f"{len(objects)} objects {zone_desc}")
        
        # Check immediate side zones
        for zone in ['immediate_left', 'immediate_right', 'immediate_far_left', 'immediate_far_right']:
            if zone in analysis['objects_by_zone'] and analysis['objects_by_zone'][zone]:
                objects = analysis['objects_by_zone'][zone]
                zone_desc = self.zones[zone]['description']
                
                if len(objects) == 1:
                    obj = objects[0]
                    color = obj.color.name if obj.color else 'unknown color'
                    shape = obj.shape.name if obj.shape else 'object'
                    advice.append(f"{color} {shape} {zone_desc}")
                elif len(objects) > 1:
                    advice.append(f"{len(objects)} objects {zone_desc}")
        
        # Enhanced path guidance with more precision
        clear_zones = []
        blocked_zones = []
        
        for zone in immediate_zones:
            if zone not in analysis['objects_by_zone'] or not analysis['objects_by_zone'][zone]:
                clear_zones.append(zone)
            else:
                blocked_zones.append(zone)
        
        # Generate sophisticated movement advice
        if clear_zones:
            if 'immediate_center' in clear_zones:
                # Check if sides are also clear for "straight ahead" advice
                if 'immediate_left' in clear_zones and 'immediate_right' in clear_zones:
                    advice.append("Path ahead is clear")
                else:
                    advice.append("Center path is clear")
            elif 'immediate_left' in clear_zones:
                if 'immediate_far_left' in clear_zones:
                    advice.append("Move left - wide left path available")
                else:
                    advice.append("Move slightly left")
            elif 'immediate_right' in clear_zones:
                if 'immediate_far_right' in clear_zones:
                    advice.append("Move right - wide right path available")
                else:
                    advice.append("Move slightly right")
            elif 'immediate_far_left' in clear_zones:
                advice.append("Move far left to avoid obstacles")
            elif 'immediate_far_right' in clear_zones:
                advice.append("Move far right to avoid obstacles")
        
        # Check medium distance zones for advanced planning
        mid_zones_blocked = []
        for zone in ['mid_left', 'mid_center', 'mid_right']:
            if zone in analysis['objects_by_zone'] and analysis['objects_by_zone'][zone]:
                mid_zones_blocked.append(zone)
        
        if mid_zones_blocked and not blocked_zones:  # Clear immediate but blocked ahead
            advice.append("Obstacles ahead at medium distance - plan your path")
        
        return advice
    
    def _generate_warnings(self, analysis: Dict) -> List[str]:
        """Generate enhanced safety warnings based on 5x3 grid analysis."""
        warnings = []
        
        # Critical zone warnings (immediate center - directly ahead)
        critical_objects = analysis['objects_by_zone'].get('immediate_center', [])
        if critical_objects:
            warnings.append("CAUTION: Obstacle directly ahead")
        
        # High priority zone warnings (immediate left/right)
        immediate_side_zones = ['immediate_left', 'immediate_right']
        for zone in immediate_side_zones:
            objects = analysis['objects_by_zone'].get(zone, [])
            if objects:
                zone_desc = self.zones[zone]['description']
                warnings.append(f"WARNING: Objects {zone_desc}")
        
        # Multiple object warnings with enhanced granularity
        immediate_zones = ['immediate_far_left', 'immediate_left', 'immediate_center', 'immediate_right', 'immediate_far_right']
        total_immediate = sum(len(analysis['objects_by_zone'].get(zone, [])) for zone in immediate_zones)
        
        if total_immediate >= 4:
            warnings.append("DANGER: Multiple obstacles in immediate area")
        elif total_immediate >= 2:
            warnings.append("Multiple obstacles detected nearby")
        
        # Narrow passage detection
        center_blocked = bool(analysis['objects_by_zone'].get('immediate_center', []))
        left_blocked = bool(analysis['objects_by_zone'].get('immediate_left', []))
        right_blocked = bool(analysis['objects_by_zone'].get('immediate_right', []))
        
        # Check for narrow passages
        if center_blocked and (left_blocked or right_blocked):
            if left_blocked and right_blocked:
                warnings.append("BLOCKED: No clear path ahead")
            elif left_blocked:
                warnings.append("Narrow passage: Only right side available")
            elif right_blocked:
                warnings.append("Narrow passage: Only left side available")
        
        # Far zone early warnings for planning
        far_center_objects = analysis['objects_by_zone'].get('far_center', [])
        if far_center_objects and not critical_objects:
            warnings.append("Obstacle approaching ahead - prepare to navigate")
        
        # Edge zone warnings (far left/right)
        edge_zones = ['immediate_far_left', 'immediate_far_right']
        for zone in edge_zones:
            objects = analysis['objects_by_zone'].get(zone, [])
            if objects:
                zone_desc = self.zones[zone]['description']
                warnings.append(f"Edge obstacle: {zone_desc}")
        
        return warnings
        if total_immediate >= 3:
            warnings.append("Multiple obstacles detected nearby")
        
        return warnings
    
    def provide_audio_feedback(self, analysis: Dict):
        """Provide audio feedback based on analysis with improved message variety."""
        # Skip audio feedback if no objects detected (reduces "Path ahead is clear" spam)
        if analysis['total_objects'] == 0:
            return
        
        print(f"🔊 Providing audio feedback... TTS available: {self.tts_engine is not None}")
        
        if not self.tts_engine:
            print("🔊 TTS not available, showing text feedback:")
            self._print_feedback(analysis)
            return
        
        # Priority: Warnings first, then advice
        messages = []
        
        # Add warnings (these are most important)
        for warning in analysis['warnings']:
            messages.append(warning)
            print(f"   Added warning: {warning}")
        
        # Add navigation advice only if there are warnings or important objects
        immediate_zones = ['immediate_left', 'immediate_center', 'immediate_right', 'immediate_far_left', 'immediate_far_right']
        has_immediate_objects = any(zone in analysis['zone_analysis'] for zone in immediate_zones)
        
        if has_immediate_objects or len(analysis['warnings']) > 0:
            for advice in analysis['navigation_advice'][:1]:  # Only 1 piece of advice at a time
                if not any(warning.lower() in advice.lower() for warning in analysis['warnings']):
                    messages.append(advice)
                    print(f"   Added advice: {advice}")
        
        print(f"🔊 Total messages to speak: {len(messages)}")
        
        # Speak only the most important message to avoid overwhelming
        if messages:
            most_important = messages[0]  # Warnings are added first, so they take priority
            print(f"🔊 Speaking most important message: {most_important}")
            self._speak_message(most_important)
    
    def _speak_message(self, message: str):
        """Speak a message using TTS with improved cooldown management."""
        current_time = time.time()
        
        # Different cooldown times based on message importance
        if "CAUTION" in message or "DANGER" in message:
            cooldown = 0.8  # Critical messages - short cooldown
        elif "WARNING" in message:
            cooldown = 1.0  # Important warnings - medium cooldown
        elif "Path ahead is clear" in message:
            cooldown = 3.0  # Path clear messages - longer cooldown to reduce repetition
        else:
            cooldown = 1.5  # Other messages - standard cooldown
        
        # Check cooldown to avoid spam
        if message in self.last_announcement_time:
            if current_time - self.last_announcement_time[message] < cooldown:
                return
        
        self.last_announcement_time[message] = current_time
        
        print(f"🔊 Speaking: {message}")  # Debug output
        
        if self.tts_engine:
            try:
                # Simple, reliable approach
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
                print(f"✅ Spoke: {message}")  # Debug confirmation
                
            except Exception as e:
                print(f"❌ TTS error: {e}")
                # Fallback to console output
                print(f"📢 AUDIO: {message}")
        else:
            # Fallback to console output when TTS is unavailable
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
        
        # Debug: Log navigation analysis
        if navigation_analysis['total_objects'] > 0:
            print(f"🎯 Navigation Analysis: {navigation_analysis['total_objects']} objects detected")
            print(f"   Zones with objects: {len(navigation_analysis['zone_analysis'])}")
            for zone, info in navigation_analysis['zone_analysis'].items():
                print(f"   {zone}: {info['object_count']} objects ({info['priority']} priority)")
        
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
