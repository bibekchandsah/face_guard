#!/usr/bin/env python3
"""
Performance Monitor for FaceGuard
Helps identify performance bottlenecks and system resource usage
"""

import psutil
import time
import threading
import cv2
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class PerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        self.stats = {
            'cpu_percent': [],
            'memory_percent': [],
            'camera_fps': 0,
            'frame_processing_time': []
        }
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        monitor_thread.start()
        print("🔍 Performance monitoring started...")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        print("⏹️ Performance monitoring stopped")
    
    def _monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                # Get CPU and memory usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                self.stats['cpu_percent'].append(cpu_percent)
                self.stats['memory_percent'].append(memory_percent)
                
                # Keep only last 60 readings (1 minute)
                if len(self.stats['cpu_percent']) > 60:
                    self.stats['cpu_percent'].pop(0)
                    self.stats['memory_percent'].pop(0)
                
                time.sleep(1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def test_camera_performance(self, duration=10):
        """Test camera capture performance"""
        print(f"📹 Testing camera performance for {duration} seconds...")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        frame_count = 0
        start_time = time.time()
        processing_times = []
        
        while time.time() - start_time < duration:
            frame_start = time.time()
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Simulate basic processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            frame_end = time.time()
            processing_time = (frame_end - frame_start) * 1000  # ms
            processing_times.append(processing_time)
            
            frame_count += 1
        
        cap.release()
        
        # Calculate statistics
        total_time = time.time() - start_time
        fps = frame_count / total_time
        avg_processing_time = sum(processing_times) / len(processing_times)
        max_processing_time = max(processing_times)
        
        print(f"📊 Camera Performance Results:")
        print(f"   FPS: {fps:.2f}")
        print(f"   Frames processed: {frame_count}")
        print(f"   Avg processing time: {avg_processing_time:.2f}ms")
        print(f"   Max processing time: {max_processing_time:.2f}ms")
        
        return {
            'fps': fps,
            'avg_processing_time': avg_processing_time,
            'max_processing_time': max_processing_time
        }
    
    def test_face_detection_performance(self, duration=10):
        """Test face detection performance"""
        print(f"👤 Testing face detection performance for {duration} seconds...")
        
        try:
            import face_recognition
            import mediapipe as mp
        except ImportError as e:
            print(f"❌ Missing dependencies: {e}")
            return
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        mp_face = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        
        frame_count = 0
        face_detection_times = []
        mediapipe_times = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                continue
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Test face_recognition
            face_start = time.time()
            try:
                boxes = face_recognition.face_locations(rgb, model="hog")
                face_end = time.time()
                face_detection_times.append((face_end - face_start) * 1000)
            except Exception:
                pass
            
            # Test MediaPipe
            mp_start = time.time()
            try:
                results = mp_face.process(rgb)
                mp_end = time.time()
                mediapipe_times.append((mp_end - mp_start) * 1000)
            except Exception:
                pass
            
            frame_count += 1
        
        cap.release()
        
        # Calculate statistics
        if face_detection_times:
            avg_face_time = sum(face_detection_times) / len(face_detection_times)
            max_face_time = max(face_detection_times)
        else:
            avg_face_time = max_face_time = 0
        
        if mediapipe_times:
            avg_mp_time = sum(mediapipe_times) / len(mediapipe_times)
            max_mp_time = max(mediapipe_times)
        else:
            avg_mp_time = max_mp_time = 0
        
        print(f"📊 Face Detection Performance Results:")
        print(f"   Face Recognition avg: {avg_face_time:.2f}ms")
        print(f"   Face Recognition max: {max_face_time:.2f}ms")
        print(f"   MediaPipe avg: {avg_mp_time:.2f}ms")
        print(f"   MediaPipe max: {max_mp_time:.2f}ms")
        
        return {
            'face_recognition_avg': avg_face_time,
            'face_recognition_max': max_face_time,
            'mediapipe_avg': avg_mp_time,
            'mediapipe_max': max_mp_time
        }
    
    def get_system_info(self):
        """Get system information"""
        print("💻 System Information:")
        print(f"   CPU cores: {psutil.cpu_count()}")
        print(f"   CPU frequency: {psutil.cpu_freq().current:.0f} MHz")
        print(f"   Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"   Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
        
        # Check if camera is being used by other processes
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    h, w = frame.shape[:2]
                    print(f"   Camera resolution: {w}x{h}")
                else:
                    print("   Camera: Accessible but no frame")
                cap.release()
            else:
                print("   Camera: Not accessible (may be in use)")
        except Exception as e:
            print(f"   Camera error: {e}")
    
    def print_current_stats(self):
        """Print current performance statistics"""
        if not self.stats['cpu_percent']:
            print("No performance data available")
            return
        
        avg_cpu = sum(self.stats['cpu_percent']) / len(self.stats['cpu_percent'])
        avg_memory = sum(self.stats['memory_percent']) / len(self.stats['memory_percent'])
        
        print(f"📈 Current Performance:")
        print(f"   CPU usage: {avg_cpu:.1f}%")
        print(f"   Memory usage: {avg_memory:.1f}%")
    
    def run_full_test(self):
        """Run comprehensive performance test"""
        print("🚀 Running Full Performance Test")
        print("=" * 50)
        
        # System info
        self.get_system_info()
        print()
        
        # Start monitoring
        self.start_monitoring()
        
        # Camera performance
        camera_results = self.test_camera_performance(5)
        print()
        
        # Face detection performance
        face_results = self.test_face_detection_performance(5)
        print()
        
        # Wait a bit for system monitoring
        print("⏳ Monitoring system for 5 seconds...")
        time.sleep(5)
        
        # Print final stats
        self.print_current_stats()
        
        # Stop monitoring
        self.stop_monitoring()
        
        print("\n" + "=" * 50)
        print("🎯 Performance Recommendations:")
        
        if camera_results and camera_results['fps'] < 15:
            print("⚠️  Low camera FPS detected - consider:")
            print("   - Closing other camera applications")
            print("   - Reducing camera resolution")
            print("   - Using performance mode in FaceGuard")
        
        if face_results:
            if face_results['face_recognition_avg'] > 100:
                print("⚠️  Slow face recognition - consider:")
                print("   - Using MediaPipe fallback mode")
                print("   - Reducing detection frequency")
            
            if face_results['mediapipe_avg'] > 50:
                print("⚠️  Slow MediaPipe processing - consider:")
                print("   - Reducing camera resolution")
                print("   - Enabling performance mode")
        
        avg_cpu = sum(self.stats['cpu_percent']) / len(self.stats['cpu_percent']) if self.stats['cpu_percent'] else 0
        if avg_cpu > 80:
            print("⚠️  High CPU usage detected - consider:")
            print("   - Closing unnecessary applications")
            print("   - Using performance mode")
            print("   - Reducing preview quality")

def main():
    monitor = PerformanceMonitor()
    
    print("🔧 FaceGuard Performance Monitor")
    print("=" * 40)
    print("Choose an option:")
    print("1. Full performance test")
    print("2. Camera performance only")
    print("3. Face detection performance only")
    print("4. System information only")
    print("5. Real-time monitoring")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        monitor.run_full_test()
    elif choice == "2":
        monitor.test_camera_performance()
    elif choice == "3":
        monitor.test_face_detection_performance()
    elif choice == "4":
        monitor.get_system_info()
    elif choice == "5":
        monitor.start_monitoring()
        try:
            print("Press Ctrl+C to stop monitoring...")
            while True:
                time.sleep(5)
                monitor.print_current_stats()
                print()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()