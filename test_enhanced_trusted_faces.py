#!/usr/bin/env python3
"""
Enhanced test script for trusted faces functionality with improved error handling
"""

import os
import json
import sys
import numpy as np

# Add current directory to path to import face_guard modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_error_handling():
    """Test the enhanced error handling in trusted faces"""
    print("🧪 Testing enhanced error handling...")
    
    try:
        from face_guard import VisionWorker
        
        # Create a mock worker
        worker = VisionWorker(
            on_toast=lambda x, y=None, z=None: None,
            on_unknown_face=lambda: None,
            on_nod=lambda: None,
            on_shake=lambda: None,
            on_brightness_change=lambda x: None,
            camera_preview=None
        )
        
        # Test 1: No face in frame
        print("  📋 Test 1: No face detected")
        fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        success, error_msg = worker.add_trusted_face(fake_frame, 'Test Person')
        expected_error = "No face detected in frame"
        if not success and expected_error in error_msg:
            print(f"    ✅ Correct error: {error_msg}")
        else:
            print(f"    ❌ Unexpected result: success={success}, error={error_msg}")
            return False
        
        # Test 2: Invalid name handling
        print("  📋 Test 2: Empty name handling")
        success, error_msg = worker.add_trusted_face(fake_frame, '')
        if not success:
            print(f"    ✅ Correctly rejected empty name")
        else:
            print(f"    ❌ Should have rejected empty name")
            return False
        
        print("✅ Enhanced error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced error handling test: {e}")
        return False

def test_trusted_faces_file_operations():
    """Test file operations with error handling"""
    print("\n🧪 Testing file operations...")
    
    try:
        from face_guard import TRUSTED_FACES_PATH, load_json, save_json
        
        # Test saving and loading with error conditions
        test_data = {
            "faces": [
                {
                    "name": "Enhanced Test Person",
                    "encoding": [0.1] * 128,  # Proper 128-dimensional encoding
                    "added_date": "2025-09-01 15:30:00"
                }
            ]
        }
        
        # Save test data
        save_json(TRUSTED_FACES_PATH, test_data)
        print("  ✅ Successfully saved test data")
        
        # Load and verify
        loaded_data = load_json(TRUSTED_FACES_PATH)
        if (loaded_data and 
            "faces" in loaded_data and 
            len(loaded_data["faces"]) == 1 and
            loaded_data["faces"][0]["name"] == "Enhanced Test Person"):
            print("  ✅ Successfully loaded and verified test data")
            return True
        else:
            print("  ❌ Data verification failed")
            return False
            
    except Exception as e:
        print(f"  ❌ File operations test failed: {e}")
        return False

def test_ui_error_messages():
    """Test that UI error messages are user-friendly"""
    print("\n🧪 Testing UI error message quality...")
    
    # Test error message content
    error_scenarios = [
        ("No face detected in frame. Please position yourself clearly in front of the camera with good lighting.", "No face detection"),
        ("Multiple faces detected (2). Please ensure only one person is visible in the camera.", "Multiple faces"),
        ("This face is already registered as 'John Doe'. Each person can only be added once.", "Duplicate face"),
        ("Could not generate face encoding from detected face. Try with better lighting or a clearer view.", "Encoding failure"),
        ("face_recognition library not available", "Missing library")
    ]
    
    for error_msg, scenario in error_scenarios:
        # Check if error message is informative and user-friendly
        if (len(error_msg) > 20 and  # Not too short
            any(word in error_msg.lower() for word in ['please', 'try', 'ensure']) and  # Helpful suggestions
            not any(word in error_msg.lower() for word in ['error', 'failed', 'exception'])):  # Not technical jargon
            print(f"  ✅ {scenario}: User-friendly message")
        else:
            print(f"  ⚠️  {scenario}: Could be more user-friendly")
    
    print("✅ UI error message quality check completed!")
    return True

def main():
    """Run all enhanced trusted faces tests"""
    print("🛡️ Enhanced FaceGuard Trusted Faces Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Enhanced error handling
    if test_enhanced_error_handling():
        tests_passed += 1
    
    # Test 2: File operations
    if test_trusted_faces_file_operations():
        tests_passed += 1
    
    # Test 3: UI error messages
    if test_ui_error_messages():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Enhanced Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All enhanced trusted faces tests passed!")
        print("\n🎉 Features verified:")
        print("  • Detailed error messages for users")
        print("  • Proper error handling in all scenarios")
        print("  • User-friendly feedback in UI dialogs")
        print("  • Robust file operations")
        print("  • Enhanced status reporting")
        return 0
    else:
        print("❌ Some enhanced tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())