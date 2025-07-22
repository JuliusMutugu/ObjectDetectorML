import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/vision_service.dart';
import '../widgets/feature_card.dart';
import '../widgets/stats_widget.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Vision AI'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () => Navigator.pushNamed(context, '/settings'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome header
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(24.0),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).colorScheme.primary,
                    Theme.of(context).colorScheme.secondary,
                  ],
                ),
                borderRadius: BorderRadius.circular(16.0),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome to Vision AI',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Advanced computer vision at your fingertips',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 24),
            
            // Stats widget
            Consumer<VisionService>(
              builder: (context, visionService, child) {
                return StatsWidget(
                  objectsDetected: visionService.totalObjectsDetected,
                  facesDetected: visionService.totalFacesDetected,
                  gesturesRecognized: visionService.totalGesturesRecognized,
                );
              },
            ),
            
            SizedBox(height: 24),
            
            // Feature cards
            Text(
              'Features',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            
            GridView.count(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              children: [
                FeatureCard(
                  title: 'Object Detection',
                  description: 'Detect and identify colored objects in real-time',
                  icon: Icons.center_focus_strong,
                  color: Colors.blue,
                  onTap: () => _startObjectDetection(context),
                ),
                FeatureCard(
                  title: 'Face Detection',
                  description: 'Detect faces and facial landmarks',
                  icon: Icons.face,
                  color: Colors.green,
                  onTap: () => _startFaceDetection(context),
                ),
                FeatureCard(
                  title: 'Hand Tracking',
                  description: 'Track hand movements and recognize gestures',
                  icon: Icons.back_hand,
                  color: Colors.orange,
                  onTap: () => _startHandTracking(context),
                ),
                FeatureCard(
                  title: 'Interactive Mode',
                  description: 'Control screen elements with hand gestures',
                  icon: Icons.touch_app,
                  color: Colors.purple,
                  onTap: () => _startInteractiveMode(context),
                ),
              ],
            ),
            
            SizedBox(height: 24),
            
            // Quick start button
            Container(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _quickStart(context),
                icon: Icon(Icons.play_arrow),
                label: Text('Quick Start - All Features'),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  textStyle: TextStyle(fontSize: 18),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  void _startObjectDetection(BuildContext context) {
    final visionService = Provider.of<VisionService>(context, listen: false);
    visionService.setDetectionMode(DetectionMode.objects);
    Navigator.pushNamed(context, '/camera');
  }
  
  void _startFaceDetection(BuildContext context) {
    final visionService = Provider.of<VisionService>(context, listen: false);
    visionService.setDetectionMode(DetectionMode.faces);
    Navigator.pushNamed(context, '/camera');
  }
  
  void _startHandTracking(BuildContext context) {
    final visionService = Provider.of<VisionService>(context, listen: false);
    visionService.setDetectionMode(DetectionMode.hands);
    Navigator.pushNamed(context, '/camera');
  }
  
  void _startInteractiveMode(BuildContext context) {
    final visionService = Provider.of<VisionService>(context, listen: false);
    visionService.setDetectionMode(DetectionMode.interactive);
    Navigator.pushNamed(context, '/camera');
  }
  
  void _quickStart(BuildContext context) {
    final visionService = Provider.of<VisionService>(context, listen: false);
    visionService.setDetectionMode(DetectionMode.all);
    Navigator.pushNamed(context, '/camera');
  }
}
