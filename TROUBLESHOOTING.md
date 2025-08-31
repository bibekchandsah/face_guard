# 🔧 FaceGuard Troubleshooting Guide

## ✅ Fixed Issues

### 1. System Tray Icon Warning
**Issue**: `QSystemTrayIcon::setVisible: No Icon set`
**Fix**: Added a programmatically created blue circle icon for the system tray

### 2. OpenCV Pose Estimation Error
**Issue**: `DLT algorithm needs at least 6 points for pose estimation`
**Fix**: 
- Added 6th landmark point (chin) for proper pose estimation
- Implemented fallback gesture detection using simple landmark positions
- Added proper error handling for pose estimation failures

### 3. Threading Timer Error
**Issue**: `QObject::startTimer: Timers cannot be started from another thread`
**Fix**: Made toast notifications thread-safe using `QTimer.singleShot`

### 4. TensorFlow/MediaPipe Warnings
**Issue**: Various TensorFlow and MediaPipe startup warnings
**Fix**: Added environment variables to suppress non-critical warnings

## 🚀 Current Status

The application now runs successfully with:
- ✅ Face detection and registration working
- ✅ Gesture recognition (nod/shake) functional
- ✅ Brightness control operational
- ✅ System tray integration working
- ✅ Toast notifications displaying properly
- ✅ Hotkeys responding correctly

## ⚠️ Expected Warnings (Normal)

These warnings are normal and don't affect functionality:
```
UserWarning: pkg_resources is deprecated...
INFO: Created TensorFlow Lite XNNPACK delegate for CPU
WARNING: All log messages before absl::InitializeLog() is called...
W0000 ... inference_feedback_manager.cc:114] Feedback manager requires...
W0000 ... landmark_projection_calculator.cc:186] Using NORM_RECT without...
```

## 🎮 How to Use

1. **Start the app**: `python face_guard.py` or `python setup_and_run.py`
2. **First time**: Look at camera to register your face
3. **System tray**: Right-click the blue circle icon for options
4. **Hotkeys**: 
   - `Ctrl+Shift+R` - Restore brightness
   - `Ctrl+Shift+L` - Toggle logs window

## 🔍 Testing Components

Run `python test_face_guard.py` to verify all components work correctly.

## 🐛 Common Issues & Solutions

### Camera Not Working
- Close other applications using the camera
- Check camera permissions in Windows settings
- Try running as administrator

### Brightness Control Not Working
- Ensure you're on the primary display
- Some external monitors may not support software brightness control
- Try adjusting display settings manually first

### Face Recognition Issues
- Ensure good lighting when registering
- Delete `~/.face_guard/user_face_encoding.json` to re-register
- The app will work with MediaPipe fallback even if face_recognition fails

### Gesture Detection Not Responsive
- Make clear, deliberate head movements
- Ensure your face is well-lit and clearly visible
- Try adjusting the gesture thresholds in the code if needed

## 📁 File Locations

- **Settings**: `~/.face_guard/`
- **Face data**: `~/.face_guard/user_face_encoding.json`
- **Logs**: Available in the GUI logs window

## 🔄 Reset Instructions

To completely reset the application:
1. Close FaceGuard
2. Delete the `~/.face_guard/` folder
3. Restart the application to re-register your face