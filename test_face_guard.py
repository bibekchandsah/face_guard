#!/usr/bin/env python3
"""
Quick test script for FaceGuard components
"""

import os
import sys

# Set environment variables to reduce warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    try:
        import screen_brightness_control as sbc
        print("✅ Screen brightness control imported successfully")
    except ImportError as e:
        print(f"❌ Screen brightness control import failed: {e}")
        return False
    
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 imported successfully")
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False
    
    try:
        import face_recognition
        print("✅ Face recognition imported successfully")
    except ImportError as e:
        print(f"❌ Face recognition import failed: {e}")
        return False
    
    try:
        import keyboard
        print("✅ Keyboard imported successfully")
    except ImportError as e:
        print(f"❌ Keyboard import failed: {e}")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    print("\nTesting camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                print(f"✅ Camera working - Frame size: {frame.shape}")
                return True
            else:
                print("❌ Camera opened but no frame captured")
                return False
        else:
            print("❌ Cannot open camera")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_brightness():
    """Test brightness control"""
    print("\nTesting brightness control...")
    try:
        import screen_brightness_control as sbc
        current = sbc.get_brightness(display=0)
        print(f"✅ Current brightness: {current}%")
        return True
    except Exception as e:
        print(f"❌ Brightness control failed: {e}")
        return False

def test_face_detection():
    """Test face detection with a single frame"""
    print("\nTesting face detection...")
    try:
        import cv2
        import mediapipe as mp
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera for face detection test")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("❌ Cannot capture frame for face detection test")
            return False
        
        # Test MediaPipe
        mp_face = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, 
            refine_landmarks=True, 
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_face.process(rgb)
        
        if results.multi_face_landmarks:
            print(f"✅ MediaPipe detected {len(results.multi_face_landmarks)} face(s)")
        else:
            print("⚠️ MediaPipe: No faces detected (this is normal if no one is in front of camera)")
        
        # Test face_recognition if available
        try:
            import face_recognition
            boxes = face_recognition.face_locations(rgb, model="hog")
            if boxes:
                print(f"✅ face_recognition detected {len(boxes)} face(s)")
            else:
                print("⚠️ face_recognition: No faces detected (this is normal if no one is in front of camera)")
        except Exception as e:
            print(f"⚠️ face_recognition test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Face detection test failed: {e}")
        return False

def main():
    print("🧪 FaceGuard Component Tests")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test camera
    if not test_camera():
        all_passed = False
    
    # Test brightness
    if not test_brightness():
        all_passed = False
    
    # Test face detection
    if not test_face_detection():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! FaceGuard should work properly.")
        print("\nYou can now run: python face_guard.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 40)

if __name__ == "__main__":
    main()