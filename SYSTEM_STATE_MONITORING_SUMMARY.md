# System State Monitoring Improvements

## Overview
Enhanced FaceGuard to properly pause monitoring when the PC is locked or in sleep mode, and resume when the system becomes active again.

## Key Improvements

### 1. Enhanced System State Detection
- **Improved Lock Detection**: Uses multiple methods to detect Windows lock screen
  - Desktop access checking
  - Desktop name verification (detects "winlogon" and secure desktop)
  - Screen saver state checking
- **Better Sleep Detection**: Enhanced power state monitoring
  - System power status checking
  - Power saving mode detection

### 2. Smart Pause/Resume Logic
- **Automatic Pausing**: Program automatically pauses monitoring when:
  - System is locked (Windows lock screen)
  - System enters sleep/hibernate mode
- **Automatic Resuming**: Program resumes monitoring when:
  - System is unlocked AND not sleeping
  - System wakes up AND not locked
- **State Coordination**: Prevents conflicts between lock and sleep states

### 3. Resource Management
- **Camera Resource Handling**: 
  - Releases camera when paused to avoid conflicts
  - Reinitializes camera when resuming
  - Handles camera reconnection gracefully
- **State Reset**: Clears all monitoring states when pausing/resuming:
  - Owner absence tracking
  - Auto-lock sequences
  - Gesture detection states
  - Brightness dimming states

### 4. User Feedback
- **Toast Notifications**: Clear status messages for:
  - 🔒 System locked - Monitoring paused
  - 🔓 System unlocked - Monitoring resumed  
  - 😴 System sleeping - Monitoring paused
  - ⏰ System awake - Monitoring resumed
- **Detailed Logging**: Comprehensive logs for debugging and monitoring

## Technical Implementation

### System State Monitoring
```python
def check_system_state(self):
    """Check system state and pause/resume program accordingly"""
    current_locked = is_system_locked()
    current_sleeping = is_system_sleeping()
    
    # Handle lock state changes
    if current_locked != self.system_locked:
        # Pause when locked, resume when unlocked (if not sleeping)
    
    # Handle sleep state changes  
    if current_sleeping != self.system_sleeping:
        # Pause when sleeping, resume when awake (if not locked)
```

### Enhanced Detection Functions
```python
def is_system_locked():
    """Multi-method Windows lock detection"""
    # Method 1: Desktop access check
    # Method 2: Desktop name verification
    # Method 3: Screen saver state check

def is_system_sleeping():
    """Enhanced sleep/power state detection"""
    # System power status monitoring
    # Power saving mode detection
```

### Main Loop Integration
```python
def run(self):
    while self.running:
        # Check system state first
        self.check_system_state()
        
        # Skip processing if paused
        if self.program_paused:
            # Release camera resources
            # Wait and recheck system state
            # Reinitialize camera when resuming
            continue
```

## Benefits

1. **Resource Efficiency**: No unnecessary camera access when system is locked/sleeping
2. **System Stability**: Prevents conflicts with system power management
3. **User Experience**: Seamless pause/resume with clear status feedback
4. **Battery Life**: Reduces power consumption when system is inactive
5. **Security**: Maintains security monitoring only when system is active

## Usage

The improvements are automatic and require no user configuration. The system will:

1. **Detect** when Windows is locked or entering sleep mode
2. **Pause** all face monitoring and camera access
3. **Resume** monitoring when the system becomes active again
4. **Notify** the user of state changes via toast messages

## Testing

Use the included test script to verify system state detection:
```bash
python test_system_state.py
```

This will show real-time system state detection and help verify the improvements work correctly on your system.

## Files Modified

- `face_guard.py`: Main program with enhanced system state monitoring
- `test_system_state.py`: Test script for verifying system state detection
- `system_state_patch.py`: Patch script used to apply improvements

## Compatibility

- **Windows 10/11**: Full compatibility with enhanced lock/sleep detection
- **Older Windows**: Basic compatibility with fallback detection methods
- **Hardware**: Works with all camera types and power management configurations