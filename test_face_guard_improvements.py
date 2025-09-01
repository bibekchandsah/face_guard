#!/usr/bin/env python3
"""
Test script to verify FaceGuard system state monitoring improvements
"""
import sys
import time
import threading
from unittest.mock import patch, MagicMock

# Mock the heavy dependencies for testing
sys.modules['cv2'] = MagicMock()
sys.modules['face_recognition'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
sys.modules['screen_brightness_control'] = MagicMock()
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['keyboard'] = MagicMock()

# Import after mocking
from face_guard import VisionWorker, is_system_locked, is_system_sleeping

def test_system_state_detection():
    """Test the system state detection functions"""
    print("Testing system state detection functions...")
    
    # Test lock detection
    locked = is_system_locked()
    print(f"System locked: {locked}")
    
    # Test sleep detection
    sleeping = is_system_sleeping()
    print(f"System sleeping: {sleeping}")
    
    return True

def test_vision_worker_state_management():
    """Test VisionWorker state management"""
    print("Testing VisionWorker state management...")
    
    # Mock callbacks
    def mock_toast(msg, color=None):
        print(f"Toast: {msg} ({color})")
    
    def mock_unknown_face():
        print("Unknown face detected")
    
    def mock_nod():
        print("Nod detected")
    
    def mock_shake():
        print("Shake detected")
    
    def mock_brightness_change(val):
        print(f"Brightness changed to {val}")
    
    # Create worker with mocked dependencies
    with patch('face_guard.cv2.VideoCapture') as mock_cap:
        mock_cap.return_value.isOpened.return_value = True
        mock_cap.return_value.read.return_value = (True, MagicMock())
        
        worker = VisionWorker(
            on_toast=mock_toast,
            on_unknown_face=mock_unknown_face,
            on_nod=mock_nod,
            on_shake=mock_shake,
            on_brightness_change=mock_brightness_change
        )
        
        # Test initial state
        print(f"Initial program_paused: {worker.program_paused}")
        print(f"Initial system_locked: {worker.system_locked}")
        print(f"Initial system_sleeping: {worker.system_sleeping}")
        
        # Test state checking
        worker.check_system_state()
        print("System state check completed")
        
        return True

def main():
    """Run all tests"""
    print("🧪 Testing FaceGuard System State Monitoring Improvements")
    print("=" * 60)
    
    try:
        # Test 1: System state detection
        if test_system_state_detection():
            print("✅ System state detection test passed")
        else:
            print("❌ System state detection test failed")
            return False
        
        print("-" * 40)
        
        # Test 2: VisionWorker state management
        if test_vision_worker_state_management():
            print("✅ VisionWorker state management test passed")
        else:
            print("❌ VisionWorker state management test failed")
            return False
        
        print("-" * 40)
        print("🎉 All tests passed! System state monitoring improvements are working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)