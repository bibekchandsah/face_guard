#!/usr/bin/env python3
"""
Gesture Testing Script for FaceGuard
This script helps test nod and shake gestures independently
"""

import os
import time
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import math

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class GestureTester:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_face = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True, 
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        
        # Gesture detection buffers
        self.pitch_hist = deque(maxlen=30)  # ~1 sec at ~30fps
        self.yaw_hist = deque(maxlen=30)
        
        print("🎯 FaceGuard Gesture Tester")
        print("=" * 40)
        print("This tool helps you test and calibrate gesture detection")
        print("Press 'q' to quit, 'n' to test nod, 's' to test shake")
        print("=" * 40)
    
    def _estimate_head_angles(self, frame_bgr):
        """Estimate head angles using MediaPipe landmarks"""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.mp_face.process(rgb)
        if not res.multi_face_landmarks:
            return None, None

        lm = res.multi_face_landmarks[0].landmark
        h, w = frame_bgr.shape[:2]

        # Try pose estimation first
        try:
            # Use 6 landmark points for proper pose estimation
            idxs = [1, 33, 263, 61, 291, 10]  # nose tip, left eye outer, right eye outer, mouth left/right, chin
            pts2d = np.array([(lm[i].x * w, lm[i].y * h) for i in idxs], dtype=np.float32)

            # Corresponding 3D model points
            pts3d = np.array([
                [0.0, 0.0, 0.0],        # nose tip
                [-30.0, -30.0, -30.0],  # left eye outer
                [30.0, -30.0, -30.0],   # right eye outer
                [-25.0, 30.0, -20.0],   # mouth left
                [25.0, 30.0, -20.0],    # mouth right
                [0.0, 50.0, -10.0],     # chin
            ], dtype=np.float32)

            cam_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
            dist = np.zeros((4,1))
            
            ok, rvec, tvec = cv2.solvePnP(pts3d, pts2d, cam_matrix, dist, flags=cv2.SOLVEPNP_ITERATIVE)
            if ok:
                rot,_ = cv2.Rodrigues(rvec)
                sy = math.sqrt(rot[0,0]**2 + rot[1,0]**2)
                singular = sy < 1e-6
                if not singular:
                    pitch = math.degrees(math.atan2(-rot[2,0], sy))   # up/down
                    yaw   = math.degrees(math.atan2(rot[1,0], rot[0,0]))  # left/right
                else:
                    pitch = math.degrees(math.atan2(rot[0,1], rot[1,1]))
                    yaw   = 0.0
                return pitch, yaw
        except (cv2.error, Exception):
            pass
        
        # Fallback: Simple landmark-based estimation
        try:
            nose_y = lm[1].y
            forehead_y = lm[10].y
            pitch = (nose_y - forehead_y) * 180
            
            face_center_x = (lm[33].x + lm[263].x) / 2
            nose_x = lm[1].x
            yaw = (nose_x - face_center_x) * 180
            
            return pitch, yaw
        except Exception:
            return None, None
    
    def _detect_gesture(self):
        """Detect nod and shake gestures"""
        PITCH_T = 12.0
        YAW_T = 15.0

        def count_oscillations(seq, th):
            states = []
            for v in seq:
                if v > th:
                    states.append(1)
                elif v < -th:
                    states.append(-1)
                else:
                    states.append(0)
            
            count = 0
            last = 0
            for s in states:
                if s != 0 and s != last and last != 0:
                    count += 1
                if s != 0:
                    last = s
            return count

        nod_osc = count_oscillations(list(self.pitch_hist), PITCH_T)
        shake_osc = count_oscillations(list(self.yaw_hist), YAW_T)

        return nod_osc >= 2, shake_osc >= 2
    
    def run_test(self, test_type, duration=10):
        """Run a specific gesture test"""
        print(f"\n🧪 Testing {test_type.upper()} gesture")
        print(f"You have {duration} seconds to perform the gesture")
        
        if test_type == "nod":
            print("👆👇 NOD your head UP and DOWN twice")
        else:
            print("👈👉 SHAKE your head LEFT and RIGHT twice")
        
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        self.pitch_hist.clear()
        self.yaw_hist.clear()
        start_time = time.time()
        detected = False
        
        print("🎬 Recording... perform the gesture now!")
        
        while time.time() - start_time < duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Get head angles
            pitch, yaw = self._estimate_head_angles(frame)
            if pitch is not None:
                self.pitch_hist.append(pitch)
                self.yaw_hist.append(yaw)
            
            # Check for gesture
            is_nod, is_shake = self._detect_gesture()
            
            # Display current angles
            if pitch is not None and yaw is not None:
                cv2.putText(frame, f"Pitch: {pitch:.1f}°", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Yaw: {yaw:.1f}°", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show detection status
            if test_type == "nod" and is_nod:
                cv2.putText(frame, "NOD DETECTED! ✓", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                detected = True
                break
            elif test_type == "shake" and is_shake:
                cv2.putText(frame, "SHAKE DETECTED! ✓", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                detected = True
                break
            elif test_type == "nod" and is_shake:
                cv2.putText(frame, "SHAKE detected (wrong gesture)", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            elif test_type == "shake" and is_nod:
                cv2.putText(frame, "NOD detected (wrong gesture)", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show remaining time
            remaining = duration - (time.time() - start_time)
            cv2.putText(frame, f"Time: {remaining:.1f}s", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow("Gesture Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        
        # Results
        if detected:
            print(f"✅ {test_type.upper()} gesture test PASSED!")
        else:
            print(f"❌ {test_type.upper()} gesture test FAILED - no gesture detected")
            print("💡 Tips:")
            if test_type == "nod":
                print("   - Make clear up-and-down head movements")
                print("   - Nod at least twice within the time limit")
                print("   - Ensure good lighting on your face")
            else:
                print("   - Make clear left-and-right head movements")
                print("   - Shake at least twice within the time limit")
                print("   - Keep your face visible to the camera")
        
        return detected
    
    def run_interactive(self):
        """Run interactive gesture testing"""
        if not self.cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        while True:
            print("\n" + "=" * 40)
            print("Choose a test:")
            print("  'n' - Test NOD gesture (up/down)")
            print("  's' - Test SHAKE gesture (left/right)")
            print("  'c' - Continuous monitoring")
            print("  'q' - Quit")
            print("=" * 40)
            
            choice = input("Enter your choice: ").lower().strip()
            
            if choice == 'q':
                break
            elif choice == 'n':
                self.run_test("nod")
            elif choice == 's':
                self.run_test("shake")
            elif choice == 'c':
                self.continuous_monitor()
            else:
                print("Invalid choice. Please try again.")
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("👋 Gesture tester closed")
    
    def continuous_monitor(self):
        """Continuously monitor head movements"""
        print("\n📹 Continuous monitoring mode")
        print("Move your head to see real-time angle measurements")
        print("Press 'q' to return to menu")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            pitch, yaw = self._estimate_head_angles(frame)
            if pitch is not None:
                self.pitch_hist.append(pitch)
                self.yaw_hist.append(yaw)
            
            is_nod, is_shake = self._detect_gesture()
            
            # Display info
            if pitch is not None and yaw is not None:
                cv2.putText(frame, f"Pitch: {pitch:.1f}°", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Yaw: {yaw:.1f}°", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if is_nod:
                cv2.putText(frame, "NOD DETECTED", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            elif is_shake:
                cv2.putText(frame, "SHAKE DETECTED", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            
            cv2.putText(frame, "Press 'q' to exit", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            cv2.imshow("Continuous Monitor", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()

def main():
    tester = GestureTester()
    tester.run_interactive()

if __name__ == "__main__":
    main()