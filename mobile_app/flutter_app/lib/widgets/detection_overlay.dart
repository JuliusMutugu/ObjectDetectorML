import 'package:flutter/material.dart';
import '../services/vision_service.dart';

class DetectionOverlay extends StatelessWidget {
  final List<DetectedObject> detections;
  final List<Face> faces;
  final List<Hand> hands;
  final List<Gesture> gestures;
  final DetectionMode detectionMode;

  const DetectionOverlay({
    Key? key,
    required this.detections,
    required this.faces,
    required this.hands,
    required this.gestures,
    required this.detectionMode,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size.infinite,
      painter: DetectionPainter(
        detections: detections,
        faces: faces,
        hands: hands,
        gestures: gestures,
        detectionMode: detectionMode,
      ),
    );
  }
}

class DetectionPainter extends CustomPainter {
  final List<DetectedObject> detections;
  final List<Face> faces;
  final List<Hand> hands;
  final List<Gesture> gestures;
  final DetectionMode detectionMode;

  DetectionPainter({
    required this.detections,
    required this.faces,
    required this.hands,
    required this.gestures,
    required this.detectionMode,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Draw objects
    if (detectionMode == DetectionMode.objects || detectionMode == DetectionMode.all) {
      _drawObjects(canvas, size);
    }

    // Draw faces
    if (detectionMode == DetectionMode.faces || detectionMode == DetectionMode.all) {
      _drawFaces(canvas, size);
    }

    // Draw hands
    if (detectionMode == DetectionMode.hands || 
        detectionMode == DetectionMode.interactive || 
        detectionMode == DetectionMode.all) {
      _drawHands(canvas, size);
    }

    // Draw gestures
    if (detectionMode == DetectionMode.interactive || detectionMode == DetectionMode.all) {
      _drawGestures(canvas, size);
    }
  }

  void _drawObjects(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    for (final detection in detections) {
      // Get color for object
      paint.color = _getColorForObjectColor(detection.color);

      // Draw bounding box
      final rect = Rect.fromLTWH(
        detection.boundingBox.x * size.width,
        detection.boundingBox.y * size.height,
        detection.boundingBox.width * size.width,
        detection.boundingBox.height * size.height,
      );
      canvas.drawRect(rect, paint);

      // Draw label
      textPainter.text = TextSpan(
        text: '${detection.color} (${(detection.confidence * 100).toInt()}%)',
        style: TextStyle(
          color: paint.color,
          fontSize: 14,
          fontWeight: FontWeight.bold,
          shadows: [
            Shadow(
              offset: Offset(1, 1),
              blurRadius: 2,
              color: Colors.black54,
            ),
          ],
        ),
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(rect.left, rect.top - textPainter.height - 4),
      );
    }
  }

  void _drawFaces(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.green
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    for (final face in faces) {
      // Draw bounding box
      final rect = Rect.fromLTWH(
        face.boundingBox.x * size.width,
        face.boundingBox.y * size.height,
        face.boundingBox.width * size.width,
        face.boundingBox.height * size.height,
      );
      canvas.drawRect(rect, paint);

      // Draw label
      textPainter.text = TextSpan(
        text: 'Face (${(face.confidence * 100).toInt()}%)',
        style: TextStyle(
          color: Colors.green,
          fontSize: 14,
          fontWeight: FontWeight.bold,
          shadows: [
            Shadow(
              offset: Offset(1, 1),
              blurRadius: 2,
              color: Colors.black54,
            ),
          ],
        ),
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(rect.left, rect.top - textPainter.height - 4),
      );
    }
  }

  void _drawHands(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.fill
      ..strokeWidth = 4.0;

    final linePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    for (final hand in hands) {
      final color = hand.side == 'left' ? Colors.blue : Colors.red;
      paint.color = color;
      linePaint.color = color;

      // Draw hand landmarks
      for (int i = 0; i < hand.landmarks.length; i++) {
        final landmark = hand.landmarks[i];
        final point = Offset(
          landmark.x * size.width,
          landmark.y * size.height,
        );
        canvas.drawCircle(point, 3, paint);
      }

      // Draw hand connections (simplified skeleton)
      _drawHandConnections(canvas, size, hand, linePaint);

      // Draw hand label
      if (hand.landmarks.isNotEmpty) {
        final wrist = hand.landmarks[0];
        textPainter.text = TextSpan(
          text: '${hand.side.toUpperCase()} (${(hand.confidence * 100).toInt()}%)',
          style: TextStyle(
            color: color,
            fontSize: 12,
            fontWeight: FontWeight.bold,
            shadows: [
              Shadow(
                offset: Offset(1, 1),
                blurRadius: 2,
                color: Colors.black54,
              ),
            ],
          ),
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(
            wrist.x * size.width,
            wrist.y * size.height - textPainter.height - 8,
          ),
        );
      }
    }
  }

  void _drawHandConnections(Canvas canvas, Size size, Hand hand, Paint paint) {
    // Simplified hand skeleton connections
    final connections = [
      [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
      [0, 5], [5, 6], [6, 7], [7, 8], // Index finger
      [0, 9], [9, 10], [10, 11], [11, 12], // Middle finger
      [0, 13], [13, 14], [14, 15], [15, 16], // Ring finger
      [0, 17], [17, 18], [18, 19], [19, 20], // Pinky
    ];

    for (final connection in connections) {
      if (connection[0] < hand.landmarks.length && connection[1] < hand.landmarks.length) {
        final start = hand.landmarks[connection[0]];
        final end = hand.landmarks[connection[1]];
        
        canvas.drawLine(
          Offset(start.x * size.width, start.y * size.height),
          Offset(end.x * size.width, end.y * size.height),
          paint,
        );
      }
    }
  }

  void _drawGestures(Canvas canvas, Size size) {
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    for (final gesture in gestures) {
      // Find the hand for this gesture
      final hand = hands.where((h) => h.id == gesture.handId).firstOrNull;
      if (hand == null || hand.landmarks.isEmpty) continue;

      final wrist = hand.landmarks[0];
      final gestureColor = _getGestureColor(gesture.type);

      // Draw gesture label
      textPainter.text = TextSpan(
        text: gesture.type.toUpperCase(),
        style: TextStyle(
          color: gestureColor,
          fontSize: 16,
          fontWeight: FontWeight.bold,
          shadows: [
            Shadow(
              offset: Offset(1, 1),
              blurRadius: 3,
              color: Colors.black87,
            ),
          ],
        ),
      );
      textPainter.layout();
      
      // Position gesture label above the hand
      textPainter.paint(
        canvas,
        Offset(
          wrist.x * size.width - textPainter.width / 2,
          wrist.y * size.height - 50,
        ),
      );
    }
  }

  Color _getColorForObjectColor(String colorName) {
    switch (colorName.toLowerCase()) {
      case 'red':
        return Colors.red;
      case 'green':
        return Colors.green;
      case 'blue':
        return Colors.blue;
      case 'yellow':
        return Colors.yellow;
      case 'orange':
        return Colors.orange;
      case 'purple':
        return Colors.purple;
      case 'pink':
        return Colors.pink;
      case 'brown':
        return Colors.brown;
      case 'black':
        return Colors.grey[800]!;
      case 'white':
        return Colors.grey[300]!;
      case 'gray':
      case 'grey':
        return Colors.grey;
      default:
        return Colors.cyan;
    }
  }

  Color _getGestureColor(String gestureType) {
    switch (gestureType.toLowerCase()) {
      case 'point':
        return Colors.yellow;
      case 'thumbs_up':
        return Colors.green;
      case 'thumbs_down':
        return Colors.red;
      case 'peace':
        return Colors.blue;
      case 'fist':
        return Colors.orange;
      case 'open_palm':
        return Colors.purple;
      default:
        return Colors.white;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}

extension FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull {
    return isEmpty ? null : first;
  }
}
