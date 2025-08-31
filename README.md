# 🛡️ FaceGuard

A Python-based security application that monitors your webcam for unknown faces and dims your screen brightness when strangers are detected, requiring gesture confirmation.

## ✨ Features

- **Face Registration**: Automatically registers your face on first startup
- **Real-time Monitoring**: Continuously monitors webcam for unknown faces
- **Camera Preview**: Live camera feed showing detection status and face boxes (optimized to prevent lag)
- **Unknown Face Logging**: Automatically saves images of unknown faces with timestamps
- **Owner Presence Detection**: Automatically dims screen to 0% when owner leaves camera view
- **Gesture Confirmation**: Uses head gestures (nod/shake) to confirm brightness changes
- **Gesture Testing**: Built-in tools to test and calibrate nod/shake detection
- **Smart Brightness Control**: Dims to 25% when unknown face detected, 0% when owner absent
- **System Tray Integration**: Runs quietly in the background
- **Real-time Logs**: Track all events and detections
- **Hotkey Support**: Quick access to all features via keyboard shortcuts

## 🚀 Quick Start

1. **Install and Run**:
   ```bash
   python setup_and_run.py
   ```

2. **First Time Setup**:
   - Look at your camera when prompted to register your face
   - The app will save your face encoding for future sessions

3. **Usage**:
   - App runs in system tray (look for the icon)
   - When an unknown face is detected, you'll see a notification
   - **Nod twice** (up and down) to confirm brightness reduction
   - **Shake twice** (left and right) to cancel
   - Use **Ctrl+Shift+R** to instantly restore brightness

## 🎮 Controls

### Hotkeys
- `Ctrl+Shift+R` - Restore brightness to normal
- `Ctrl+Shift+L` - Toggle logs window
- `Ctrl+Shift+C` - Toggle camera preview window

### System Tray Menu
- **Status** - Check current app status
- **Show Logs** - View real-time activity logs
- **Show Camera Preview** - View live camera feed with face detection
- **View Unknown Faces** - Open folder containing captured unknown face images
- **Restore Brightness** - Restore normal brightness
- **Exit** - Close the application

### Camera Preview Features
- **Live Feed**: See exactly what the camera captures (optimized for performance)
- **Face Detection Boxes**: Green box for owner, red for unknown faces
- **Status Overlay**: Real-time owner presence indicator
- **Reset Owner Face**: Button to re-register your face if needed
- **Gesture Testing**: Test nod and shake detection with real-time feedback
- **Unknown Face Viewer**: Quick access to folder containing captured images

## 🧪 Testing Gestures

Use the standalone gesture tester to calibrate and test your head movements:

```bash
python test_gestures.py
```

This interactive tool helps you:
- Test nod detection (up/down head movement)
- Test shake detection (left/right head movement)  
- Monitor real-time head angle measurements
- Calibrate gesture sensitivity

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

## 🔒 Privacy & Security

- All face data is stored locally in `~/.face_guard/`
- No data is sent to external servers
- Face encodings are mathematical representations, not images
- You can delete the face data anytime by removing the `.face_guard` folder

## 🐛 Troubleshooting

### Camera Issues
- Ensure no other applications are using the camera
- Check camera permissions in your OS settings
- Try running as administrator (Windows) if camera access fails

### Brightness Control Issues
- On Linux, you may need to install additional packages for brightness control
- On macOS, ensure accessibility permissions are granted

### Face Recognition Issues
- Ensure good lighting when registering your face
- If recognition is poor, delete `~/.face_guard/user_face_encoding.json` to re-register
- The app uses both robust face-recognition and fallback landmark matching

## 📝 Logs Location

Logs and settings are stored in:
- Windows: `C:\Users\[username]\.face_guard\`
- Linux/macOS: `~/.face_guard/`

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve FaceGuard!