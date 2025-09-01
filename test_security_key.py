#!/usr/bin/env python3
"""
Test script for security key functionality
"""

import os
import json
import sys
import time

# Add current directory to path to import face_guard modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_security_key_file_operations():
    """Test security key file operations"""
    print("🧪 Testing security key file operations...")
    
    try:
        from face_guard import (
            set_security_key, verify_security_key, start_trusted_session,
            end_trusted_session, get_security_key_status, SECURITY_KEY_PATH
        )
        
        # Clean up any existing security key file
        if os.path.exists(SECURITY_KEY_PATH):
            os.remove(SECURITY_KEY_PATH)
        
        # Test 1: Set security key
        print("  📋 Test 1: Setting security key")
        success, message = set_security_key("test123", 5)  # 5 minute timeout
        if success:
            print(f"    ✅ Security key set: {message}")
        else:
            print(f"    ❌ Failed to set security key: {message}")
            return False
        
        # Test 2: Verify correct key
        print("  📋 Test 2: Verifying correct key")
        success, message = verify_security_key("test123")
        if success:
            print(f"    ✅ Key verified: {message}")
        else:
            print(f"    ❌ Key verification failed: {message}")
            return False
        
        # Test 3: Verify incorrect key
        print("  📋 Test 3: Verifying incorrect key")
        success, message = verify_security_key("wrong123")
        if not success:
            print(f"    ✅ Correctly rejected wrong key: {message}")
        else:
            print(f"    ❌ Should have rejected wrong key")
            return False
        
        # Test 4: Start trusted session
        print("  📋 Test 4: Starting trusted session")
        success, message = start_trusted_session("Test User")
        if success:
            print(f"    ✅ Session started: {message}")
        else:
            print(f"    ❌ Failed to start session: {message}")
            return False
        
        # Test 5: Check status
        print("  📋 Test 5: Checking security status")
        status = get_security_key_status()
        if (status['enabled'] and status['configured'] and 
            status['session_active'] and status['trusted_user'] == "Test User"):
            print(f"    ✅ Status correct: Session active for {status['trusted_user']}")
        else:
            print(f"    ❌ Status incorrect: {status}")
            return False
        
        # Test 6: End session
        print("  📋 Test 6: Ending trusted session")
        success, message = end_trusted_session()
        if success:
            print(f"    ✅ Session ended: {message}")
        else:
            print(f"    ❌ Failed to end session: {message}")
            return False
        
        # Test 7: Verify session ended
        print("  📋 Test 7: Verifying session ended")
        status = get_security_key_status()
        if not status['session_active']:
            print(f"    ✅ Session correctly ended")
        else:
            print(f"    ❌ Session should be ended: {status}")
            return False
        
        print("✅ All security key file operations tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in security key file operations test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_security_key_json_structure():
    """Test the security key JSON file structure"""
    print("\n🧪 Testing security key JSON structure...")
    
    try:
        from face_guard import SECURITY_KEY_PATH, load_json
        
        # Check if file exists
        if not os.path.exists(SECURITY_KEY_PATH):
            print("  ❌ Security key file not found")
            return False
        
        # Load and verify structure
        data = load_json(SECURITY_KEY_PATH)
        
        required_fields = [
            "security_key_hash", "security_key_enabled", "security_key_timeout",
            "trusted_session_active", "trusted_session_start", "trusted_user_name",
            "last_updated", "creation_date"
        ]
        
        for field in required_fields:
            if field not in data:
                print(f"  ❌ Missing required field: {field}")
                return False
        
        print("  ✅ All required fields present")
        print(f"  📄 File location: {SECURITY_KEY_PATH}")
        print(f"  📊 Data structure: {len(data)} fields")
        
        # Display current data (without sensitive info)
        safe_data = data.copy()
        if safe_data.get("security_key_hash"):
            safe_data["security_key_hash"] = "[HIDDEN]"
        
        print(f"  📋 Current data: {json.dumps(safe_data, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in JSON structure test: {e}")
        return False

def test_security_key_timeout():
    """Test security key timeout functionality"""
    print("\n🧪 Testing security key timeout...")
    
    try:
        from face_guard import (
            set_security_key, start_trusted_session, check_trusted_session_timeout,
            get_security_key_status
        )
        
        # Set a very short timeout for testing (1 second)
        print("  📋 Setting 1-second timeout for testing")
        success, message = set_security_key("timeout_test", 0.017)  # ~1 second
        if not success:
            print(f"  ❌ Failed to set timeout key: {message}")
            return False
        
        # Start session
        success, message = start_trusted_session("Timeout Test User")
        if not success:
            print(f"  ❌ Failed to start session: {message}")
            return False
        
        print("  ⏳ Waiting for timeout...")
        time.sleep(2)  # Wait for timeout
        
        # Check if session timed out
        timed_out, message = check_trusted_session_timeout()
        if timed_out:
            print(f"  ✅ Session correctly timed out: {message}")
        else:
            print(f"  ❌ Session should have timed out: {message}")
            return False
        
        # Verify session is no longer active
        status = get_security_key_status()
        if not status['session_active']:
            print("  ✅ Session correctly marked as inactive")
        else:
            print("  ❌ Session should be inactive after timeout")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in timeout test: {e}")
        return False

def main():
    """Run all security key tests"""
    print("🔑 FaceGuard Security Key Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: File operations
    if test_security_key_file_operations():
        tests_passed += 1
    
    # Test 2: JSON structure
    if test_security_key_json_structure():
        tests_passed += 1
    
    # Test 3: Timeout functionality
    if test_security_key_timeout():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Security Key Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All security key tests passed!")
        print("\n🎉 Features verified:")
        print("  • Security key creation and storage")
        print("  • Key verification and authentication")
        print("  • Trusted session management")
        print("  • Session timeout handling")
        print("  • JSON file structure and persistence")
        print("  • Status reporting and monitoring")
        return 0
    else:
        print("❌ Some security key tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())