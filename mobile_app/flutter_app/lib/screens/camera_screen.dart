import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:provider/provider.dart';
import '../services/vision_service.dart';
import '../widgets/detection_overlay.dart';
import '../widgets/gesture_controls.dart';
import '../main.dart';

class CameraScreen extends StatefulWidget {
  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _cameraController;
  bool _isInitialized = false;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    if (cameras.isEmpty) {
      print('No cameras available');
      return;
    }

    _cameraController = CameraController(
      cameras.first,
      ResolutionPreset.medium,
      enableAudio: false,
    );

    try {
      await _cameraController!.initialize();
      setState(() {
        _isInitialized = true;
      });
      
      // Start processing frames
      _startFrameProcessing();
    } catch (e) {
      print('Error initializing camera: $e');
    }
  }

  void _startFrameProcessing() {
    // Process frames periodically
    Stream.periodic(Duration(milliseconds: 100)).listen((_) async {
      if (_isProcessing || !_isInitialized || _cameraController == null) return;
      
      _isProcessing = true;
      try {
        final image = await _cameraController!.takePicture();
        final visionService = Provider.of<VisionService>(context, listen: false);
        await visionService.processImage(image.path);
      } catch (e) {
        print('Error processing frame: $e');
      } finally {
        _isProcessing = false;
      }
    });
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final visionService = Provider.of<VisionService>(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(_getScreenTitle(visionService.detectionMode)),
        backgroundColor: Colors.black87,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(Icons.flip_camera_ios),
            onPressed: _flipCamera,
          ),
          IconButton(
            icon: Icon(visionService.isProcessing ? Icons.pause : Icons.play_arrow),
            onPressed: () => visionService.toggleProcessing(),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Camera preview
          if (_isInitialized && _cameraController != null)
            Container(
              width: double.infinity,
              height: double.infinity,
              child: CameraPreview(_cameraController!),
            )
          else
            Container(
              width: double.infinity,
              height: double.infinity,
              color: Colors.black,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: Colors.white),
                    SizedBox(height: 16),
                    Text(
                      'Initializing Camera...',
                      style: TextStyle(color: Colors.white),
                    ),
                  ],
                ),
              ),
            ),
          
          // Detection overlay
          if (_isInitialized)
            DetectionOverlay(
              detections: visionService.detections,
              faces: visionService.faces,
              hands: visionService.hands,
              gestures: visionService.gestures,
              detectionMode: visionService.detectionMode,
            ),
          
          // Gesture controls (only in interactive mode)
          if (visionService.detectionMode == DetectionMode.interactive ||
              visionService.detectionMode == DetectionMode.all)
            GestureControls(
              hands: visionService.hands,
              gestures: visionService.gestures,
            ),
          
          // Performance info
          Positioned(
            top: 16,
            right: 16,
            child: Container(
              padding: EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    'FPS: ${visionService.fps.toStringAsFixed(1)}',
                    style: TextStyle(color: Colors.white, fontSize: 12),
                  ),
                  Text(
                    'Objects: ${visionService.detections.length}',
                    style: TextStyle(color: Colors.white, fontSize: 12),
                  ),
                  Text(
                    'Faces: ${visionService.faces.length}',
                    style: TextStyle(color: Colors.white, fontSize: 12),
                  ),
                  Text(
                    'Hands: ${visionService.hands.length}',
                    style: TextStyle(color: Colors.white, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
          
          // Bottom controls
          Positioned(
            bottom: 32,
            left: 16,
            right: 16,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildControlButton(
                  icon: Icons.center_focus_strong,
                  label: 'Objects',
                  isActive: visionService.detectionMode == DetectionMode.objects,
                  onPressed: () => visionService.setDetectionMode(DetectionMode.objects),
                ),
                _buildControlButton(
                  icon: Icons.face,
                  label: 'Faces',
                  isActive: visionService.detectionMode == DetectionMode.faces,
                  onPressed: () => visionService.setDetectionMode(DetectionMode.faces),
                ),
                _buildControlButton(
                  icon: Icons.back_hand,
                  label: 'Hands',
                  isActive: visionService.detectionMode == DetectionMode.hands,
                  onPressed: () => visionService.setDetectionMode(DetectionMode.hands),
                ),
                _buildControlButton(
                  icon: Icons.all_inclusive,
                  label: 'All',
                  isActive: visionService.detectionMode == DetectionMode.all,
                  onPressed: () => visionService.setDetectionMode(DetectionMode.all),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required String label,
    required bool isActive,
    required VoidCallback onPressed,
  }) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? Colors.blue : Colors.black54,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.white, size: 20),
            SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(color: Colors.white, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }

  String _getScreenTitle(DetectionMode mode) {
    switch (mode) {
      case DetectionMode.objects:
        return 'Object Detection';
      case DetectionMode.faces:
        return 'Face Detection';
      case DetectionMode.hands:
        return 'Hand Tracking';
      case DetectionMode.interactive:
        return 'Interactive Mode';
      case DetectionMode.all:
        return 'All Features';
    }
  }

  Future<void> _flipCamera() async {
    if (cameras.length < 2) return;
    
    final currentCamera = _cameraController?.description;
    final newCamera = cameras.firstWhere(
      (camera) => camera != currentCamera,
      orElse: () => cameras.first,
    );
    
    await _cameraController?.dispose();
    
    _cameraController = CameraController(
      newCamera,
      ResolutionPreset.medium,
      enableAudio: false,
    );
    
    try {
      await _cameraController!.initialize();
      setState(() {});
    } catch (e) {
      print('Error flipping camera: $e');
    }
  }
}
