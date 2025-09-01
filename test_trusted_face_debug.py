#!/usr/bin/env python3
"""
Debug script for trusted faces functionality
"""

import os
import sys
import cv2
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_camera_and_face_detection():
    """Test camera access and face detection"""
    print("🧪 Testing camera access and face detection...")
    
    try:
        # Test camera access
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not accessible")
            return False
        
        print("✅ Camera accessible")
        
        # Capture a frame
        ret, frame = cap.read()
        if not ret or frame is None:
            print("❌ Could not capture frame")
            cap.release()
            return False
        
        print(f"✅ Frame captured, shape: {frame.shape}")
        
        # Test face detection with OpenCV
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        print(f"📊 OpenCV detected {len(faces)} face(s)")
        
        # Test face_recognition library
        try:
            import face_recognition
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            print(f"📊 face_recognition detected {len(boxes)} face(s)")
            
            if boxes:
                encodings = face_recognition.face_encodings(rgb, boxes)
                print(f"📊 Generated {len(encodings)} face encoding(s)")
                if encodings:
                    print(f"📊 First encoding shape: {encodings[0].shape}")
                    print("✅ Face recognition working properly")
                else:
                    print("❌ Could not generate face encodings")
            else:
                print("ℹ️  No faces detected by face_recognition (try positioning yourself in front of camera)")
                
        except ImportError:
            print("❌ face_recognition library not available")
            cap.release()
            return False
        except Exception as e:
            print(f"❌ Error with face_recognition: {e}")
            cap.release()
            return False
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_trusted_face_workflow():
    """Test the trusted face workflow"""
    print("\n🧪 Testing trusted face workflow...")
    
    try:
        from face_guard import VisionWorker, HAS_FACE_REC
        
        if not HAS_FACE_REC:
            print("❌ face_recognition library not available")
            return False
        
        print("✅ face_recognition library available")
        
        # Create a mock worker
        worker = VisionWorker(
            on_toast=lambda msg, color=None: print(f"Toast: {msg}"),
            on_unknown_face=lambda: None,
            on_nod=lambda: None,
            on_shake=lambda: None,
            on_brightness_change=lambda val: None,
            camera_preview=None
        )
        
        print(f"✅ Worker created, trusted faces count: {len(worker.trusted_faces)}")
        
        # Test with a dummy frame (this won't work for real face detection, but tests the workflow)
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # This should fail gracefully
        result = worker.add_trusted_face(dummy_frame, "Test Person")
        print(f"📊 add_trusted_face with dummy frame result: {result} (expected: False)")
        
        print("✅ Trusted face workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Trusted face workflow test failed: {e}")
        return False

def main():
    """Run debug tests"""
    print("🛡️ FaceGuard Trusted Faces Debug")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Camera and face detection
    if test_camera_and_face_detection():
        tests_passed += 1
    
    # Test 2: Trusted face workflow
    if test_trusted_face_workflow():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Debug Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All debug tests passed!")
        print("\n💡 Tips for using trusted faces:")
        print("   1. Make sure you're clearly visible in the camera")
        print("   2. Ensure good lighting")
        print("   3. Only one face should be visible when adding")
        print("   4. Face should be looking towards the camera")
        return 0
    else:
        print("❌ Some debug tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())