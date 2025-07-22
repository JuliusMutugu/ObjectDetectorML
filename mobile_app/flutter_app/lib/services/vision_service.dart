import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

enum DetectionMode {
  objects,
  faces,
  hands,
  interactive,
  all,
}

class DetectedObject {
  final String id;
  final String color;
  final double confidence;
  final BoundingBox boundingBox;

  DetectedObject({
    required this.id,
    required this.color,
    required this.confidence,
    required this.boundingBox,
  });

  factory DetectedObject.fromJson(Map<String, dynamic> json) {
    return DetectedObject(
      id: json['id'] ?? '',
      color: json['color'] ?? 'unknown',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      boundingBox: BoundingBox.fromJson(json['bounding_box'] ?? {}),
    );
  }
}

class BoundingBox {
  final double x;
  final double y;
  final double width;
  final double height;

  BoundingBox({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
  });

  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      x: (json['x'] ?? 0.0).toDouble(),
      y: (json['y'] ?? 0.0).toDouble(),
      width: (json['width'] ?? 0.0).toDouble(),
      height: (json['height'] ?? 0.0).toDouble(),
    );
  }
}

class Face {
  final String id;
  final double confidence;
  final BoundingBox boundingBox;
  final Map<String, dynamic> landmarks;

  Face({
    required this.id,
    required this.confidence,
    required this.boundingBox,
    required this.landmarks,
  });

  factory Face.fromJson(Map<String, dynamic> json) {
    return Face(
      id: json['id'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      boundingBox: BoundingBox.fromJson(json['bounding_box'] ?? {}),
      landmarks: json['landmarks'] ?? {},
    );
  }
}

class Hand {
  final String id;
  final String side; // 'left' or 'right'
  final double confidence;
  final List<Landmark> landmarks;

  Hand({
    required this.id,
    required this.side,
    required this.confidence,
    required this.landmarks,
  });

  factory Hand.fromJson(Map<String, dynamic> json) {
    final landmarksList = json['landmarks'] as List? ?? [];
    return Hand(
      id: json['id'] ?? '',
      side: json['side'] ?? 'unknown',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      landmarks: landmarksList.map((l) => Landmark.fromJson(l)).toList(),
    );
  }
}

class Landmark {
  final double x;
  final double y;
  final double z;

  Landmark({
    required this.x,
    required this.y,
    required this.z,
  });

  factory Landmark.fromJson(Map<String, dynamic> json) {
    return Landmark(
      x: (json['x'] ?? 0.0).toDouble(),
      y: (json['y'] ?? 0.0).toDouble(),
      z: (json['z'] ?? 0.0).toDouble(),
    );
  }
}

class Gesture {
  final String type;
  final double confidence;
  final String handId;

  Gesture({
    required this.type,
    required this.confidence,
    required this.handId,
  });

  factory Gesture.fromJson(Map<String, dynamic> json) {
    return Gesture(
      type: json['type'] ?? 'unknown',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      handId: json['hand_id'] ?? '',
    );
  }
}

class VisionService extends ChangeNotifier {
  static const String baseUrl = 'http://127.0.0.1:8000';
  
  DetectionMode _detectionMode = DetectionMode.objects;
  bool _isProcessing = false;
  double _fps = 0.0;
  
  List<DetectedObject> _detections = [];
  List<Face> _faces = [];
  List<Hand> _hands = [];
  List<Gesture> _gestures = [];
  
  // Session statistics
  int _totalObjectsDetected = 0;
  int _totalFacesDetected = 0;
  int _totalGesturesRecognized = 0;
  
  Timer? _fpsTimer;
  int _frameCount = 0;
  
  // Getters
  DetectionMode get detectionMode => _detectionMode;
  bool get isProcessing => _isProcessing;
  double get fps => _fps;
  List<DetectedObject> get detections => _detections;
  List<Face> get faces => _faces;
  List<Hand> get hands => _hands;
  List<Gesture> get gestures => _gestures;
  int get totalObjectsDetected => _totalObjectsDetected;
  int get totalFacesDetected => _totalFacesDetected;
  int get totalGesturesRecognized => _totalGesturesRecognized;
  
  VisionService() {
    _startFpsCounter();
  }
  
  void _startFpsCounter() {
    _fpsTimer = Timer.periodic(Duration(seconds: 1), (timer) {
      _fps = _frameCount.toDouble();
      _frameCount = 0;
      notifyListeners();
    });
  }
  
  void setDetectionMode(DetectionMode mode) {
    _detectionMode = mode;
    notifyListeners();
  }
  
  void toggleProcessing() {
    _isProcessing = !_isProcessing;
    notifyListeners();
  }
  
  Future<void> processImage(String imagePath) async {
    if (!_isProcessing) return;
    
    try {
      _frameCount++;
      
      switch (_detectionMode) {
        case DetectionMode.objects:
          await _detectObjects(imagePath);
          break;
        case DetectionMode.faces:
          await _detectFaces(imagePath);
          break;
        case DetectionMode.hands:
          await _detectHands(imagePath);
          break;
        case DetectionMode.interactive:
          await _detectHands(imagePath);
          await _detectGestures(imagePath);
          break;
        case DetectionMode.all:
          await _detectAll(imagePath);
          break;
      }
      
      notifyListeners();
    } catch (e) {
      print('Error processing image: $e');
    }
  }
  
  Future<void> _detectObjects(String imagePath) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/detect/objects'));
      request.files.add(await http.MultipartFile.fromPath('file', imagePath));
      
      final response = await request.send();
      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final data = json.decode(responseBody);
        
        _detections = (data['objects'] as List)
            .map((obj) => DetectedObject.fromJson(obj))
            .toList();
        
        // Update statistics
        _totalObjectsDetected += _detections.length;
      }
    } catch (e) {
      print('Error detecting objects: $e');
    }
  }
  
  Future<void> _detectFaces(String imagePath) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/detect/faces'));
      request.files.add(await http.MultipartFile.fromPath('file', imagePath));
      
      final response = await request.send();
      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final data = json.decode(responseBody);
        
        _faces = (data['faces'] as List)
            .map((face) => Face.fromJson(face))
            .toList();
        
        // Update statistics
        _totalFacesDetected += _faces.length;
      }
    } catch (e) {
      print('Error detecting faces: $e');
    }
  }
  
  Future<void> _detectHands(String imagePath) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/detect/hands'));
      request.files.add(await http.MultipartFile.fromPath('file', imagePath));
      
      final response = await request.send();
      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final data = json.decode(responseBody);
        
        _hands = (data['hands'] as List)
            .map((hand) => Hand.fromJson(hand))
            .toList();
      }
    } catch (e) {
      print('Error detecting hands: $e');
    }
  }
  
  Future<void> _detectGestures(String imagePath) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/detect/gestures'));
      request.files.add(await http.MultipartFile.fromPath('file', imagePath));
      
      final response = await request.send();
      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final data = json.decode(responseBody);
        
        _gestures = (data['gestures'] as List)
            .map((gesture) => Gesture.fromJson(gesture))
            .toList();
        
        // Update statistics
        _totalGesturesRecognized += _gestures.length;
      }
    } catch (e) {
      print('Error detecting gestures: $e');
    }
  }
  
  Future<void> _detectAll(String imagePath) async {
    await Future.wait([
      _detectObjects(imagePath),
      _detectFaces(imagePath),
      _detectHands(imagePath),
      _detectGestures(imagePath),
    ]);
  }
  
  @override
  void dispose() {
    _fpsTimer?.cancel();
    super.dispose();
  }
}
