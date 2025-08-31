#!/usr/bin/env python3
"""
Setup and run script for FaceGuard application.
This script handles installation of dependencies and launches the app.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_camera():
    """Quick camera test"""
    print("Testing camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera access successful!")
                return True
        print("❌ Camera not accessible")
        return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def main():
    print("🛡️  FaceGuard Setup & Launch")
    print("=" * 40)
    
    # Set environment variables to reduce warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return
    
    # Install requirements
    if not install_requirements():
        print("Please fix installation issues and try again.")
        return
    
    # Test camera
    if not check_camera():
        print("⚠️  Camera issues detected. The app may not work properly.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    print("\n🚀 Launching FaceGuard...")
    print("Hotkeys:")
    print("  Ctrl+Shift+R - Restore brightness")
    print("  Ctrl+Shift+L - Toggle logs window")
    print("\nRight-click system tray icon for options.")
    print("Note: Some startup warnings are normal and can be ignored.")
    print("=" * 40)
    
    # Launch the main application
    try:
        import face_guard
        face_guard.main()
    except KeyboardInterrupt:
        print("\n👋 FaceGuard stopped by user")
    except Exception as e:
        print(f"❌ Error running FaceGuard: {e}")
        print("Check the logs window for more details.")

if __name__ == "__main__":
    main()