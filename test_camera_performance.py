#!/usr/bin/env python3
"""
Camera Performance Test
Quick test to verify camera preview optimization
"""

import cv2
import time
import threading
from collections import deque

class PerformanceTest:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.fps_counter = deque(maxlen=30)
        self.running = True
        
    def test_basic_capture(self):
        """Test basic camera capture performance"""
        print("🧪 Testing basic camera capture...")
        
        frame_count = 0
        start_time = time.time()
        
        for i in range(100):  # Test 100 frames
            ret, frame = self.cap.read()
            if ret:
                frame_count += 1
                # Simulate basic processing
                frame = cv2.flip(frame, 1)
                cv2.putText(frame, f"Frame {i}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        print(f"✅ Basic capture: {fps:.1f} FPS ({frame_count} frames in {elapsed:.2f}s)")
        return fps
    
    def test_threaded_capture(self):
        """Test threaded camera capture"""
        print("🧪 Testing threaded camera capture...")
        
        frames_processed = 0
        start_time = time.time()
        
        def capture_thread():
            nonlocal frames_processed
            while frames_processed < 100:
                ret, frame = self.cap.read()
                if ret:
                    frames_processed += 1
                    # Simulate processing
                    frame = cv2.flip(frame, 1)
                    cv2.putText(frame, f"Threaded {frames_processed}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                time.sleep(0.01)  # Simulate 100 FPS max
        
        thread = threading.Thread(target=capture_thread)
        thread.start()
        thread.join()
        
        elapsed = time.time() - start_time
        fps = frames_processed / elapsed
        
        print(f"✅ Threaded capture: {fps:.1f} FPS ({frames_processed} frames in {elapsed:.2f}s)")
        return fps
    
    def test_optimized_capture(self):
        """Test optimized capture with minimal processing"""
        print("🧪 Testing optimized camera capture...")
        
        frame_count = 0
        start_time = time.time()
        last_frame = None
        
        for i in range(100):
            ret, frame = self.cap.read()
            if ret:
                frame_count += 1
                # Minimal processing - just flip
                if i % 2 == 0:  # Process every other frame
                    last_frame = cv2.flip(frame, 1)
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        print(f"✅ Optimized capture: {fps:.1f} FPS ({frame_count} frames in {elapsed:.2f}s)")
        return fps
    
    def run_tests(self):
        """Run all performance tests"""
        print("🚀 Camera Performance Tests")
        print("=" * 40)
        
        if not self.cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        # Test different approaches
        basic_fps = self.test_basic_capture()
        threaded_fps = self.test_threaded_capture()
        optimized_fps = self.test_optimized_capture()
        
        print("\n📊 Results Summary:")
        print(f"Basic FPS:     {basic_fps:.1f}")
        print(f"Threaded FPS:  {threaded_fps:.1f}")
        print(f"Optimized FPS: {optimized_fps:.1f}")
        
        # Performance recommendations
        print("\n💡 Recommendations:")
        if optimized_fps > basic_fps * 1.2:
            print("✅ Optimization effective - use optimized approach")
        else:
            print("⚠️  Basic approach sufficient")
            
        if threaded_fps > basic_fps * 1.1:
            print("✅ Threading beneficial")
        else:
            print("⚠️  Threading overhead not worth it")
        
        self.cap.release()

if __name__ == "__main__":
    test = PerformanceTest()
    test.run_tests()