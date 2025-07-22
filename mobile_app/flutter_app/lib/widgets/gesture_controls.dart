import 'package:flutter/material.dart';
import '../services/vision_service.dart';

class GestureControls extends StatelessWidget {
  final List<Hand> hands;
  final List<Gesture> gestures;

  const GestureControls({
    Key? key,
    required this.hands,
    required this.gestures,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Interactive buttons that respond to gestures
        Positioned(
          top: 100,
          left: 20,
          child: _buildInteractiveButton(
            icon: Icons.play_arrow,
            label: 'Play',
            gestureType: 'point',
            onTap: () => _onButtonTapped('play'),
          ),
        ),
        Positioned(
          top: 100,
          right: 20,
          child: _buildInteractiveButton(
            icon: Icons.pause,
            label: 'Pause',
            gestureType: 'fist',
            onTap: () => _onButtonTapped('pause'),
          ),
        ),
        Positioned(
          bottom: 150,
          left: 20,
          child: _buildInteractiveButton(
            icon: Icons.thumb_up,
            label: 'Like',
            gestureType: 'thumbs_up',
            onTap: () => _onButtonTapped('like'),
          ),
        ),
        Positioned(
          bottom: 150,
          right: 20,
          child: _buildInteractiveButton(
            icon: Icons.thumb_down,
            label: 'Dislike',
            gestureType: 'thumbs_down',
            onTap: () => _onButtonTapped('dislike'),
          ),
        ),
        
        // Gesture status indicator
        Positioned(
          top: 200,
          left: 20,
          right: 20,
          child: _buildGestureStatus(),
        ),
      ],
    );
  }

  Widget _buildInteractiveButton({
    required IconData icon,
    required String label,
    required String gestureType,
    required VoidCallback onTap,
  }) {
    // Check if this gesture is currently active
    final isActive = gestures.any((g) => g.type == gestureType && g.confidence > 0.7);
    
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: Duration(milliseconds: 200),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isActive ? Colors.green.withOpacity(0.8) : Colors.black54,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isActive ? Colors.greenAccent : Colors.white30,
            width: 2,
          ),
          boxShadow: isActive
              ? [
                  BoxShadow(
                    color: Colors.green.withOpacity(0.5),
                    blurRadius: 8,
                    spreadRadius: 2,
                  ),
                ]
              : null,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: Colors.white,
              size: 24,
            ),
            SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (isActive)
              Container(
                margin: EdgeInsets.only(top: 4),
                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.greenAccent,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'ACTIVE',
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: 8,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildGestureStatus() {
    if (gestures.isEmpty) {
      return Container(
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.black54,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          'Show hand gestures to interact',
          style: TextStyle(
            color: Colors.white70,
            fontSize: 14,
          ),
          textAlign: TextAlign.center,
        ),
      );
    }

    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(
            'Active Gestures:',
            style: TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8),
          ...gestures.map((gesture) {
            final hand = hands.where((h) => h.id == gesture.handId).firstOrNull;
            return Padding(
              padding: EdgeInsets.symmetric(vertical: 2),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${hand?.side ?? 'Unknown'} ${gesture.type}',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: _getConfidenceColor(gesture.confidence),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${(gesture.confidence * 100).toInt()}%',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }

  void _onButtonTapped(String action) {
    print('Button tapped: $action');
    // Here you could trigger actual app functionality
    // For example:
    // - Play/pause media
    // - Like/dislike content
    // - Navigate between screens
    // - Trigger animations
  }
}

extension FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull {
    return isEmpty ? null : first;
  }
}
