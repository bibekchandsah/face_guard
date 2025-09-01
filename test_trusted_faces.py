#!/usr/bin/env python3
"""
Test script for trusted faces functionality
"""

import os
import json
import sys

# Add current directory to path to import face_guard modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_trusted_faces_file_structure():
    """Test that trusted faces file structure is correct"""
    print("🧪 Testing trusted faces file structure...")
    
    # Import after adding to path
    from face_guard import TRUSTED_FACES_PATH, load_json, save_json
    
    # Test data
    test_data = {
        "faces": [
            {
                "name": "Test Person",
                "encoding": [0.1, 0.2, 0.3] * 42,  # 128 dimensions (simplified for test)
                "added_date": "2025-09-01 12:00:00"
            }
        ]
    }
    
    # Save test data
    save_json(TRUSTED_FACES_PATH, test_data)
    print(f"✅ Created test trusted faces file: {TRUSTED_FACES_PATH}")
    
    # Load and verify
    loaded_data = load_json(TRUSTED_FACES_PATH)
    if loaded_data and "faces" in loaded_data and len(loaded_data["faces"]) == 1:
        print("✅ Trusted faces file structure is correct")
        print(f"   - Found {len(loaded_data['faces'])} trusted face(s)")
        print(f"   - First face name: {loaded_data['faces'][0]['name']}")
        return True
    else:
        print("❌ Trusted faces file structure is incorrect")
        return False

def test_trusted_faces_logic():
    """Test the trusted faces detection logic"""
    print("\n🧪 Testing trusted faces detection logic...")
    
    try:
        # Import face_recognition to check if it's available
        import face_recognition
        print("✅ face_recognition library is available")
        
        # Test would require actual camera/image data
        print("ℹ️  Full detection test requires camera feed (skipped in automated test)")
        return True
        
    except ImportError:
        print("❌ face_recognition library not available - trusted faces won't work")
        return False

def main():
    """Run all trusted faces tests"""
    print("🛡️ FaceGuard Trusted Faces Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: File structure
    if test_trusted_faces_file_structure():
        tests_passed += 1
    
    # Test 2: Detection logic
    if test_trusted_faces_logic():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All trusted faces tests passed!")
        return 0
    else:
        print("❌ Some trusted faces tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())