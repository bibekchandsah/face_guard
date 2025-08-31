# 📹 Camera Preview & Owner Presence Guide

## 🆕 New Features Added

### 1. **Camera Preview Window**
- **Access**: Right-click system tray → "Show Camera Preview" or press `Ctrl+Shift+C`
- **Live Feed**: See exactly what your camera captures in real-time
- **Face Detection**: Visual boxes around detected faces
  - 🟢 **Green Box** = Owner (you) detected
  - 🔴 **Red Box** = Unknown person detected
- **Status Display**: Shows "Owner Present ✅" or "Owner Not Detected ❌"

### 2. **Owner Presence-Based Brightness Control**
- **When Owner Leaves**: Brightness automatically dims to **0%** after 3 seconds
- **When Owner Returns**: Brightness automatically restores to normal level
- **Visual Feedback**: Toast notifications show when brightness changes due to presence

### 3. **Enhanced Face Management**
- **Reset Owner Face**: Button in camera preview to re-register your face
- **Better Detection**: Improved face recognition with visual feedback

## 🎮 How to Use

### Opening Camera Preview
1. **Method 1**: Right-click the blue system tray icon → "📹 Show Camera Preview"
2. **Method 2**: Press `Ctrl+Shift+C` hotkey
3. **Method 3**: The preview opens automatically on first run for setup

### Understanding the Display
- **Camera Feed**: Live video from your webcam
- **Face Boxes**: Colored rectangles around detected faces
- **Status Bar**: Shows current owner detection status
- **Control Buttons**: 
  - "Hide Preview" - Closes the window
  - "Reset Owner Face" - Clears saved face data for re-registration

### Owner Presence Behavior
1. **Owner Present**: Normal operation, brightness unchanged
2. **Owner Leaves**: 3-second countdown, then brightness → 0%
3. **Owner Returns**: Immediate brightness restoration
4. **Unknown Person**: Gesture confirmation system activates

## 🔧 Troubleshooting

### Camera Preview Issues
- **Black Screen**: Check if another app is using the camera
- **No Face Boxes**: Ensure good lighting and face the camera directly
- **Wrong Detection**: Use "Reset Owner Face" to re-register

### Owner Detection Issues
- **Not Recognizing You**: 
  - Ensure consistent lighting
  - Face the camera directly during registration
  - Click "Reset Owner Face" to start over
- **False Positives**: Adjust lighting or re-register in current conditions

### Brightness Control Issues
- **Too Sensitive**: The 3-second delay prevents accidental dimming
- **Not Restoring**: Check if manual brightness changes interfere
- **External Monitors**: Some displays may not support software brightness control

## ⚙️ Settings & Customization

### Timing Adjustments
- **Owner Absence Delay**: Currently 3 seconds (can be modified in code)
- **Gesture Timeout**: 6 seconds for nod/shake confirmation
- **Preview Update Rate**: ~30 FPS for smooth display

### Detection Sensitivity
- **Face Recognition**: Uses strict tolerance for security
- **Gesture Detection**: Requires clear head movements
- **Presence Detection**: Immediate response to owner return

## 🎯 Best Practices

1. **Good Lighting**: Ensure your face is well-lit during registration
2. **Consistent Position**: Register from your typical working position
3. **Clear Background**: Avoid busy backgrounds that might confuse detection
4. **Regular Re-registration**: Re-register if your appearance changes significantly

## 🔄 Quick Reset

If detection isn't working well:
1. Open Camera Preview (`Ctrl+Shift+C`)
2. Click "Reset Owner Face"
3. Look directly at camera for 3 seconds
4. Wait for "Face registered ✅" confirmation

The system will now recognize you with the new registration!