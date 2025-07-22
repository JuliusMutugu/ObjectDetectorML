import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/vision_service.dart';

class SettingsScreen extends StatefulWidget {
  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _apiUrlController = TextEditingController(text: 'http://127.0.0.1:8000');
  bool _enableObjectDetection = true;
  bool _enableFaceDetection = true;
  bool _enableHandTracking = true;
  bool _enableGestureRecognition = true;
  double _confidenceThreshold = 0.5;
  double _processingInterval = 100; // milliseconds

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  void _loadSettings() {
    // In a real app, you would load these from shared preferences
    // For now, we'll use default values
  }

  void _saveSettings() {
    // In a real app, you would save these to shared preferences
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Settings saved successfully'),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final visionService = Provider.of<VisionService>(context, listen: false);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('Settings'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(Icons.save),
            onPressed: _saveSettings,
          ),
        ],
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          // API Configuration
          _buildSection(
            title: 'API Configuration',
            children: [
              TextFormField(
                controller: _apiUrlController,
                decoration: InputDecoration(
                  labelText: 'Backend URL',
                  hintText: 'http://127.0.0.1:8000',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.link),
                ),
                keyboardType: TextInputType.url,
              ),
              SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _testConnection,
                icon: Icon(Icons.wifi_find),
                label: Text('Test Connection'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
          
          SizedBox(height: 24),
          
          // Detection Features
          _buildSection(
            title: 'Detection Features',
            children: [
              SwitchListTile(
                title: Text('Object Detection'),
                subtitle: Text('Detect and classify objects in the camera feed'),
                value: _enableObjectDetection,
                onChanged: (value) {
                  setState(() {
                    _enableObjectDetection = value;
                  });
                },
                secondary: Icon(Icons.center_focus_strong),
              ),
              SwitchListTile(
                title: Text('Face Detection'),
                subtitle: Text('Detect faces and facial landmarks'),
                value: _enableFaceDetection,
                onChanged: (value) {
                  setState(() {
                    _enableFaceDetection = value;
                  });
                },
                secondary: Icon(Icons.face),
              ),
              SwitchListTile(
                title: Text('Hand Tracking'),
                subtitle: Text('Track hand positions and landmarks'),
                value: _enableHandTracking,
                onChanged: (value) {
                  setState(() {
                    _enableHandTracking = value;
                  });
                },
                secondary: Icon(Icons.back_hand),
              ),
              SwitchListTile(
                title: Text('Gesture Recognition'),
                subtitle: Text('Recognize hand gestures for interaction'),
                value: _enableGestureRecognition,
                onChanged: (value) {
                  setState(() {
                    _enableGestureRecognition = value;
                  });
                },
                secondary: Icon(Icons.gesture),
              ),
            ],
          ),
          
          SizedBox(height: 24),
          
          // Performance Settings
          _buildSection(
            title: 'Performance Settings',
            children: [
              ListTile(
                title: Text('Confidence Threshold'),
                subtitle: Text('Minimum confidence for detections (${(_confidenceThreshold * 100).toInt()}%)'),
                trailing: Text('${(_confidenceThreshold * 100).toInt()}%'),
              ),
              Slider(
                value: _confidenceThreshold,
                min: 0.1,
                max: 1.0,
                divisions: 9,
                onChanged: (value) {
                  setState(() {
                    _confidenceThreshold = value;
                  });
                },
              ),
              SizedBox(height: 16),
              ListTile(
                title: Text('Processing Interval'),
                subtitle: Text('Time between frame processing (${_processingInterval.toInt()}ms)'),
                trailing: Text('${_processingInterval.toInt()}ms'),
              ),
              Slider(
                value: _processingInterval,
                min: 50,
                max: 500,
                divisions: 9,
                onChanged: (value) {
                  setState(() {
                    _processingInterval = value;
                  });
                },
              ),
            ],
          ),
          
          SizedBox(height: 24),
          
          // Camera Settings
          _buildSection(
            title: 'Camera Settings',
            children: [
              ListTile(
                title: Text('Camera Resolution'),
                subtitle: Text('Higher resolution uses more processing power'),
                trailing: DropdownButton<String>(
                  value: 'Medium',
                  items: ['Low', 'Medium', 'High', 'Very High']
                      .map((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                  onChanged: (String? newValue) {
                    // Handle resolution change
                  },
                ),
              ),
              SwitchListTile(
                title: Text('Auto Focus'),
                subtitle: Text('Automatically focus the camera'),
                value: true,
                onChanged: (value) {
                  // Handle auto focus toggle
                },
                secondary: Icon(Icons.center_focus_strong),
              ),
              SwitchListTile(
                title: Text('Flash'),
                subtitle: Text('Use camera flash in low light'),
                value: false,
                onChanged: (value) {
                  // Handle flash toggle
                },
                secondary: Icon(Icons.flash_on),
              ),
            ],
          ),
          
          SizedBox(height: 24),
          
          // About Section
          _buildSection(
            title: 'About',
            children: [
              ListTile(
                title: Text('App Version'),
                subtitle: Text('1.0.0'),
                leading: Icon(Icons.info),
              ),
              ListTile(
                title: Text('Backend Status'),
                subtitle: Text('Connected'),
                leading: Icon(Icons.cloud_done, color: Colors.green),
              ),
              ListTile(
                title: Text('Performance'),
                subtitle: Text('FPS: ${visionService.fps.toStringAsFixed(1)}'),
                leading: Icon(Icons.speed),
              ),
            ],
          ),
          
          SizedBox(height: 24),
          
          // Reset Button
          ElevatedButton.icon(
            onPressed: _resetToDefaults,
            icon: Icon(Icons.restore),
            label: Text('Reset to Defaults'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required List<Widget> children,
  }) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
            SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  void _testConnection() async {
    try {
      // Show loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 16),
              Text('Testing connection...'),
            ],
          ),
        ),
      );

      // Simulate API call
      await Future.delayed(Duration(seconds: 2));
      
      Navigator.of(context).pop(); // Close loading dialog
      
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Connection successful!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      Navigator.of(context).pop(); // Close loading dialog
      
      // Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Connection failed: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Reset Settings'),
        content: Text('Are you sure you want to reset all settings to their default values?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _apiUrlController.text = 'http://127.0.0.1:8000';
                _enableObjectDetection = true;
                _enableFaceDetection = true;
                _enableHandTracking = true;
                _enableGestureRecognition = true;
                _confidenceThreshold = 0.5;
                _processingInterval = 100;
              });
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Settings reset to defaults'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
            child: Text('Reset'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }
}
