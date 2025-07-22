import 'package:camera/camera.dart';

class CameraService {
  static List<CameraDescription> _cameras = [];
  static bool _isInitialized = false;
  
  static Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      _cameras = await availableCameras();
      _isInitialized = true;
    } catch (e) {
      print('Error initializing cameras: $e');
    }
  }
  
  static List<CameraDescription> get cameras => _cameras;
  static bool get isInitialized => _isInitialized;
  
  static CameraDescription? get frontCamera {
    try {
      return _cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
      );
    } catch (e) {
      return null;
    }
  }
  
  static CameraDescription? get backCamera {
    try {
      return _cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
      );
    } catch (e) {
      return null;
    }
  }
}
