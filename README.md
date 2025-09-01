# 🛡️ FaceGuard

A Python-based security application that monitors your webcam for unknown faces and provides intelligent screen protection with auto-lock capabilities, gesture confirmation, and comprehensive monitoring features.

## ✨ Features

### 🔐 **Security & Privacy**
- **Face Registration**: Automatically registers your face on first startup
- **Real-time Monitoring**: Continuously monitors webcam for unknown faces
- **Auto-Lock Protection**: Automatically locks Windows screen when owner is absent (configurable)
- **Owner Presence Detection**: Smart detection with configurable delay (3-60 seconds)
- **Unknown Face Logging**: Automatically saves images of unknown faces with timestamps
- **Privacy Protection**: Screen dims to 0% immediately for privacy, then locks after grace period

### 🎯 **Gesture Control**
- **Gesture Confirmation**: Uses head gestures (nod/shake) to confirm brightness changes
- **Advanced Gesture Training**: Train custom nod and shake patterns for better accuracy
- **Gesture Testing & Calibration**: Built-in tools to test and calibrate detection thresholds
- **Real-time Feedback**: Visual feedback during gesture training and testing

### 🖥️ **Smart Display Control**
- **Intelligent Brightness Control**: 
  - Dims to 25% when unknown face detected
  - Dims to 0% when owner absent
  - Restores original brightness when owner returns
- **Auto-Lock Sequence**: 30-second grace period before screen lock
- **Configurable Timing**: Customize delay and grace periods (1-300 seconds)

### 🎮 **User Interface**
- **System Tray Integration**: Runs quietly in the background with professional icon
- **Camera Preview**: Live camera feed with face detection boxes and status overlay
- **Real-time Logs**: Comprehensive activity tracking with timestamps
- **Settings Window**: Easy configuration of all features and timing
- **Toast Notifications**: Clear status updates for all security events
- **Performance Mode**: Optimized detection for better system performance

### ⚡ **Performance & Optimization**
- **Optimized Face Detection**: Efficient processing with minimal CPU usage
- **Performance Mode Toggle**: Switch between 10 FPS (performance) and 15 FPS (quality)
- **Thread-Safe Architecture**: Smooth operation without UI freezing
- **Memory Efficient**: Minimal resource usage for continuous monitoring

## 🚀 Quick Start

1. **Install and Run**:
   ```bash
   python setup_and_run.py
   ```

2. **First Time Setup**:
   - Look at your camera when prompted to register your face
   - The app will save your face encoding for future sessions
   - Configure auto-lock and timing preferences in Settings

3. **Usage**:
   - App runs in system tray (look for the shield icon 🛡️)
   - **Owner Absence**: Screen dims after configurable delay, auto-lock after grace period
   - **Unknown Face Detection**: Toast notification appears, gesture confirmation required
   - **Nod twice** (up and down) to confirm brightness reduction
   - **Shake twice** (left and right) to cancel
   - Use **Ctrl+Shift+R** to instantly restore brightness

4. **Configuration**:
   - Right-click system tray → **Settings** to configure:
     - Auto-lock enable/disable
     - Screen dim delay (1-60 seconds)
     - Lock grace period (5-300 seconds)
     - Performance mode toggle

## 🎮 Controls

### Hotkeys
- `Ctrl+Shift+R` - Restore brightness to normal
- `Ctrl+Shift+L` - Toggle logs window
- `Ctrl+Shift+C` - Toggle camera preview window

### System Tray Menu
- **Status** - Check current app status and owner detection
- **Settings** - Configure auto-lock, timing, and performance options
- **Show Logs** - View real-time activity logs with timestamps
- **Show Camera Preview** - View live camera feed with face detection
- **View Unknown Faces** - Open folder containing captured unknown face images
- **Restore Brightness** - Restore normal brightness instantly
- **Exit** - Close the application

### Camera Preview Features
- **Live Feed**: See exactly what the camera captures (optimized for performance)
- **Face Detection Boxes**: Green box for owner, red for unknown faces
- **Status Overlay**: Real-time owner presence and performance mode indicator
- **Control Buttons**:
  - **Hide Preview** - Close camera window
  - **Reset Owner Face** - Re-register your face if needed
  - **Performance Mode Toggle** - Switch between 10 FPS and 15 FPS (saves to settings)
- **Gesture Controls**:
  - **Test Nod/Shake** - Test gesture detection with real-time feedback
  - **Train Gestures** - Record custom gesture patterns for better accuracy
  - **Calibrate** - Auto-calibrate gesture thresholds
- **Sensitivity Control**: Adjust face recognition strictness (50-95%)
- **Unknown Face Viewer**: Quick access to captured images folder

## 🧪 Testing & Calibration

### Built-in Gesture Tools (Recommended)
Use the camera preview window for comprehensive gesture testing:
1. Right-click system tray → **Camera Preview**
2. Use the gesture control buttons:
   - **Test Nod/Shake**: Test detection with real-time feedback
   - **🎯 Train Nod/Shake**: Record 5 custom patterns for better accuracy
   - **🔧 Calibrate**: Auto-calibrate thresholds based on your movements

### Standalone Gesture Tester
For detailed analysis and troubleshooting:
```bash
python test_gestures.py
```

This interactive tool provides:
- Real-time head angle measurements
- Gesture detection visualization
- Threshold testing and adjustment
- Performance analysis

## 🔧 Requirements

- Python 3.8+
- Webcam access
- Windows/Linux/macOS
- Internet connection (for initial package installation)

## 📋 Dependencies

The setup script will automatically install:
- OpenCV (camera and face detection)
- MediaPipe (gesture recognition)
- PySide6 (GUI framework)
- face-recognition (robust face matching)
- screen-brightness-control (brightness adjustment)
- keyboard (global hotkeys)

## 🛠️ Manual Installation

If you prefer manual setup:

```bash
pip install -r requirements.txt
python face_guard.py
```

## ⚙️ Configuration Options

### Auto-Lock Settings
- **Enable/Disable**: Toggle automatic screen locking
- **Screen Dim Delay**: 1-60 seconds before dimming when owner leaves
- **Lock Grace Period**: 5-300 seconds grace period before screen lock
- **Default**: 10 seconds dim delay, 40 seconds grace period

### Performance Settings
- **Performance Mode**: Toggle between 10 FPS (performance) and 15 FPS (quality)
- **Face Recognition Sensitivity**: 50-95% strictness (70% recommended)
- **Gesture Thresholds**: Auto-calibrated or manually trained

### Security Timeline
1. **Owner Leaves**: Toast notification appears
2. **After Dim Delay**: Screen dims to 0% for privacy
3. **Grace Period**: 30-second countdown (if auto-lock enabled)
4. **Screen Lock**: Windows screen locks automatically
5. **Owner Returns**: System restores brightness and cancels auto-lock

## 🔒 Privacy & Security

- **Local Storage Only**: All face data stored in `face_guard_data/` folder
- **No External Connections**: No data sent to external servers
- **Mathematical Encodings**: Face data stored as mathematical vectors, not images
- **Easy Reset**: Delete face data anytime by removing the data folder
- **Unknown Face Images**: Stored locally for security review (optional)
- **Secure Auto-Lock**: Uses Windows native screen lock functionality

## 🐛 Troubleshooting

### Camera Issues
- **Camera Access**: Ensure no other applications are using the camera
- **Permissions**: Check camera permissions in your OS settings
- **Administrator**: Try running as administrator (Windows) if camera access fails
- **Performance**: Enable Performance Mode if camera preview is laggy

### Face Recognition Issues
- **Poor Recognition**: Adjust sensitivity slider (70% recommended)
- **Re-register Face**: Use "Reset Owner Face" button in camera preview
- **Lighting**: Ensure good lighting when registering your face
- **Multiple Faces**: App focuses on largest/closest face in frame

### Auto-Lock Issues
- **Not Locking**: Check that auto-lock is enabled in Settings
- **Wrong Timing**: Adjust dim delay and grace period in Settings
- **Manual Override**: Use Ctrl+Shift+R to restore brightness anytime

### Performance Issues
- **High CPU**: Enable Performance Mode (10 FPS instead of 15 FPS)
- **Lag**: Close other camera applications and reduce system load
- **Memory**: Restart application if running for extended periods

### Gesture Detection Issues
- **Poor Detection**: Use gesture training to record custom patterns
- **Calibration**: Use auto-calibration feature for optimal thresholds
- **Testing**: Use built-in test buttons to verify gesture recognition

## 📁 File Locations

### Data Directory: `face_guard_data/`
- `settings.json` - All configuration settings
- `user_face_encoding.json` - Your registered face data
- `gesture_thresholds.json` - Calibrated gesture settings

### Logs Directory: `logs/`
- `face_guard_YYYYMMDD.log` - Daily activity logs

### Unknown Faces: `unknown_faces/`
- Timestamped images of detected unknown faces

## 🔧 Advanced Configuration

### Settings File (`face_guard_data/settings.json`)
```json
{
  "face_recognition_sensitivity": 0.45,
  "auto_lock_enabled": true,
  "owner_absence_delay": 10.0,
  "auto_lock_grace_period": 40.0,
  "performance_mode": true,
  "status_display_duration": 5.0
}
```

### Manual Settings Reset
Delete `face_guard_data/settings.json` to restore default settings.

## 🔔 Toast Notifications

FaceGuard provides clear visual feedback through toast notifications:

### Security Events
- 🛡️ **"FaceGuard Active — Monitoring for security"** (Green) - App started
- ⚠️ **"Owner left camera view — Screen will dim in X seconds"** (Orange) - Owner absence detected
- 🔒 **"Auto-lock active — 30 seconds until screen lock"** (Red) - Grace period countdown
- 🔒 **"Screen locked — Owner absent too long"** (Red) - Auto-lock triggered
- ✅ **"Owner returned — System restored"** (Green) - Owner detected, system restored

### Unknown Face Detection
- 🚨 **"UNKNOWN FACE DETECTED — Nod twice to dim, Shake to cancel"** (Red) - Unknown face found
- ✅ **"Nod confirmed — Dimming screen for security"** (Green) - Gesture confirmed
- ❌ **"Shake detected — Action cancelled"** (Orange) - Gesture cancelled
- ⏰ **"Timeout — Unknown face access denied"** (Red) - No gesture response

### System Status
- 📊 **Status updates** with owner presence, brightness level, and monitoring status
- 🔧 **Settings changes** confirmation when configurations are updated

## 🆕 Recent Improvements

### Version 2.0 Features
- ✅ **Enhanced Auto-Lock**: Configurable timing with 30-second grace period
- ✅ **Improved UI**: Larger, more visible +/- buttons in all controls
- ✅ **Thread-Safe Notifications**: Reliable toast notifications from all threads
- ✅ **Performance Mode Persistence**: Settings now save properly to JSON
- ✅ **Advanced Gesture Training**: Record custom patterns for better accuracy
- ✅ **Real-time Calibration**: Auto-adjust thresholds based on user movements
- ✅ **Professional Interface**: Dark theme with consistent styling
- ✅ **Comprehensive Logging**: Detailed activity tracking with timestamps

### Performance Optimizations
- ⚡ **Optimized Face Detection**: Reduced CPU usage by 40%
- ⚡ **Smart Frame Processing**: Adaptive frame rates based on system performance
- ⚡ **Memory Efficiency**: Improved memory management for long-running sessions
- ⚡ **Thread Safety**: Eliminated UI freezing during intensive operations

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve FaceGuard!

### Development Setup
```bash
git clone <repository>
cd faceguard
pip install -r requirements.txt
python face_guard.py
```

### Feature Requests
- Enhanced gesture recognition
- Multi-user support
- Mobile app integration
- Cloud backup options