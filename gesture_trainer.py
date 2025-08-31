#!/usr/bin/env python3
"""
FaceGuard Gesture Trainer
Interactive tool to train and calibrate gesture recognition
"""

import os
import json
import time
import math
import cv2
import numpy as np
from collections import deque
import mediapipe as mp

# Configuration - use current script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(SCRIPT_DIR, "face_guard_data")
os.makedirs(APP_DIR, exist_ok=True)

class GestureTrainer:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.mp_face = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True, 
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        
        # Gesture data
        self.pitch_hist = deque(maxlen=30)
        self.yaw_hist = deque(maxlen=30)
        self.baseline_pitch = 0.0
        self.baseline_yaw = 0.0
        
        # Training state
        self.mode = "menu"  # menu, calibrate, train_nod, train_shake, test
        self.training_data = {"nod": [], "shake": []}
        self.start_time = None
        
        # Thresholds
        self.nod_threshold = 12.0
        self.shake_threshold = 15.0
        
        # Load existing patterns
        self.load_gesture_patterns()
        
    def load_gesture_patterns(self):
        """Load saved gesture patterns"""
        patterns_path = os.path.join(APP_DIR, "gesture_patterns.json")
        if os.path.exists(patterns_path):
            with open(patterns_path, 'r') as f:
                data = json.load(f)
                self.training_data = data
                print("✅ Loaded existing gesture patterns")
        else:
            print("ℹ️  No existing patterns found")
    
    def save_gesture_patterns(self):
        """Save gesture patterns"""
        patterns_path = os.path.join(APP_DIR, "gesture_patterns.json")
        with open(patterns_path, 'w') as f:
            json.dump(self.training_data, f, indent=2)
        print("💾 Gesture patterns saved")
    
    def estimate_head_angles(self, frame):
        """Estimate head pitch and yaw angles"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_face.process(rgb)
        
        if not results.multi_face_landmarks:
            return None, None
        
        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]
        
        try:
            # Use key landmarks for pose estimation
            idxs = [1, 33, 263, 61, 291, 10]  # nose, eyes, mouth, chin
            pts2d = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in idxs], dtype=np.float32)
            
            # 3D model points
            pts3d = np.array([
                [0.0, 0.0, 0.0],        # nose tip
                [-30.0, -30.0, -30.0],  # left eye
                [30.0, -30.0, -30.0],   # right eye
                [-25.0, 30.0, -20.0],   # mouth left
                [25.0, 30.0, -20.0],    # mouth right
                [0.0, 50.0, -10.0],     # chin
            ], dtype=np.float32)
            
            # Camera matrix
            cam_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
            dist = np.zeros((4,1))
            
            success, rvec, tvec = cv2.solvePnP(pts3d, pts2d, cam_matrix, dist)
            if success:
                rot_matrix, _ = cv2.Rodrigues(rvec)
                sy = math.sqrt(rot_matrix[0,0]**2 + rot_matrix[1,0]**2)
                
                if sy > 1e-6:
                    pitch = math.degrees(math.atan2(-rot_matrix[2,0], sy))
                    yaw = math.degrees(math.atan2(rot_matrix[1,0], rot_matrix[0,0]))
                else:
                    pitch = math.degrees(math.atan2(rot_matrix[0,1], rot_matrix[1,1]))
                    yaw = 0.0
                
                return pitch, yaw
        except:
            pass
        
        return None, None
    
    def detect_gesture(self):
        """Detect nod and shake gestures"""
        if len(self.pitch_hist) < 10 or len(self.yaw_hist) < 10:
            return False, False
        
        # Apply baseline correction
        corrected_pitch = [p - self.baseline_pitch for p in self.pitch_hist]
        corrected_yaw = [y - self.baseline_yaw for y in self.yaw_hist]
        
        def count_oscillations(seq, threshold):
            states = []
            for v in seq:
                if v > threshold:
                    states.append(1)
                elif v < -threshold:
                    states.append(-1)
                else:
                    states.append(0)
            
            count = 0
            last_nonzero = 0
            for s in states:
                if s != 0 and s != last_nonzero and last_nonzero != 0:
                    count += 1
                if s != 0:
                    last_nonzero = s
            return count
        
        pitch_osc = count_oscillations(corrected_pitch, self.nod_threshold)
        yaw_osc = count_oscillations(corrected_yaw, self.shake_threshold)
        
        is_nod = pitch_osc >= 2 and yaw_osc < 2
        is_shake = yaw_osc >= 2 and pitch_osc < 2
        
        return is_nod, is_shake
    
    def draw_interface(self, frame):
        """Draw the training interface"""
        h, w = frame.shape[:2]
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (w-10, 120), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Title
        cv2.putText(frame, "FaceGuard Gesture Trainer", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Mode-specific instructions
        if self.mode == "menu":
            cv2.putText(frame, "Press: [C]alibrate | [N]od Training | [S]hake Training | [T]est | [Q]uit", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Current Thresholds - Nod: {self.nod_threshold:.1f}° | Shake: {self.shake_threshold:.1f}°", 
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(frame, f"Patterns Saved - Nod: {len(self.training_data['nod'])} | Shake: {len(self.training_data['shake'])}", 
                       (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        elif self.mode == "calibrate":
            elapsed = time.time() - self.start_time
            remaining = max(0, 3.0 - elapsed)
            cv2.putText(frame, f"🔧 CALIBRATING - Look straight ahead, don't move! ({remaining:.1f}s)", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        elif self.mode == "train_nod":
            patterns = len(self.training_data["nod"])
            cv2.putText(frame, f"🎯 NOD TRAINING - Nod up and down slowly! ({patterns}/5 patterns)", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, "Press [ESC] to stop training", (20, 85), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        elif self.mode == "train_shake":
            patterns = len(self.training_data["shake"])
            cv2.putText(frame, f"🎯 SHAKE TRAINING - Shake left and right slowly! ({patterns}/5 patterns)", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, "Press [ESC] to stop training", (20, 85), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        elif self.mode == "test":
            cv2.putText(frame, "🧪 TESTING - Try nodding or shaking your head!", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            cv2.putText(frame, "Press [ESC] to return to menu", (20, 85), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Current angles display
        if len(self.pitch_hist) > 0 and len(self.yaw_hist) > 0:
            current_pitch = self.pitch_hist[-1] - self.baseline_pitch
            current_yaw = self.yaw_hist[-1] - self.baseline_yaw
            cv2.putText(frame, f"Pitch: {current_pitch:+6.1f}° | Yaw: {current_yaw:+6.1f}°", 
                       (w-250, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def run_calibration(self):
        """Run calibration mode"""
        elapsed = time.time() - self.start_time
        
        if elapsed >= 3.0:
            if len(self.pitch_hist) > 10:
                self.baseline_pitch = sum(self.pitch_hist) / len(self.pitch_hist)
                self.baseline_yaw = sum(self.yaw_hist) / len(self.yaw_hist)
                print(f"✅ Calibration complete! Baseline - Pitch: {self.baseline_pitch:.1f}°, Yaw: {self.baseline_yaw:.1f}°")
            else:
                print("❌ Calibration failed - insufficient data")
            
            self.mode = "menu"
            self.pitch_hist.clear()
            self.yaw_hist.clear()
    
    def run_training(self, gesture_type):
        """Run gesture training"""
        if len(self.pitch_hist) > 0 and len(self.yaw_hist) > 0:
            if gesture_type == "nod":
                pitch_range = max(self.pitch_hist) - min(self.pitch_hist)
                if pitch_range > 5.0:
                    pattern = {
                        "pitch_data": list(self.pitch_hist),
                        "yaw_data": list(self.yaw_hist),
                        "pitch_range": pitch_range,
                        "timestamp": time.time()
                    }
                    self.training_data["nod"].append(pattern)
                    print(f"📊 Recorded nod pattern {len(self.training_data['nod'])}/5 (range: {pitch_range:.1f}°)")
                    
                    if len(self.training_data["nod"]) >= 5:
                        ranges = [p["pitch_range"] for p in self.training_data["nod"]]
                        avg_range = sum(ranges) / len(ranges)
                        self.nod_threshold = max(8.0, avg_range * 0.6)
                        print(f"✅ Nod training complete! New threshold: {self.nod_threshold:.1f}°")
                        self.save_gesture_patterns()
                        self.mode = "menu"
            
            elif gesture_type == "shake":
                yaw_range = max(self.yaw_hist) - min(self.yaw_hist)
                if yaw_range > 5.0:
                    pattern = {
                        "pitch_data": list(self.pitch_hist),
                        "yaw_data": list(self.yaw_hist),
                        "yaw_range": yaw_range,
                        "timestamp": time.time()
                    }
                    self.training_data["shake"].append(pattern)
                    print(f"📊 Recorded shake pattern {len(self.training_data['shake'])}/5 (range: {yaw_range:.1f}°)")
                    
                    if len(self.training_data["shake"]) >= 5:
                        ranges = [p["yaw_range"] for p in self.training_data["shake"]]
                        avg_range = sum(ranges) / len(ranges)
                        self.shake_threshold = max(10.0, avg_range * 0.6)
                        print(f"✅ Shake training complete! New threshold: {self.shake_threshold:.1f}°")
                        self.save_gesture_patterns()
                        self.mode = "menu"
    
    def run_test(self):
        """Run gesture testing"""
        is_nod, is_shake = self.detect_gesture()
        
        if is_nod:
            print("✅ NOD DETECTED!")
        elif is_shake:
            print("✅ SHAKE DETECTED!")
    
    def run(self):
        """Main training loop"""
        print("🎯 FaceGuard Gesture Trainer Started")
        print("Press 'C' to calibrate, 'N' for nod training, 'S' for shake training, 'T' to test, 'Q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Estimate head angles
            pitch, yaw = self.estimate_head_angles(frame)
            if pitch is not None:
                self.pitch_hist.append(pitch)
                self.yaw_hist.append(yaw)
            
            # Process current mode
            if self.mode == "calibrate":
                self.run_calibration()
            elif self.mode == "train_nod":
                self.run_training("nod")
            elif self.mode == "train_shake":
                self.run_training("shake")
            elif self.mode == "test":
                self.run_test()
            
            # Draw interface
            display_frame = self.draw_interface(frame)
            cv2.imshow("Gesture Trainer", display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('c') and self.mode == "menu":
                self.mode = "calibrate"
                self.start_time = time.time()
                self.pitch_hist.clear()
                self.yaw_hist.clear()
                print("🔧 Starting calibration...")
            elif key == ord('n') and self.mode == "menu":
                self.mode = "train_nod"
                self.training_data["nod"] = []  # Reset nod training
                self.pitch_hist.clear()
                self.yaw_hist.clear()
                print("🎯 Starting nod training...")
            elif key == ord('s') and self.mode == "menu":
                self.mode = "train_shake"
                self.training_data["shake"] = []  # Reset shake training
                self.pitch_hist.clear()
                self.yaw_hist.clear()
                print("🎯 Starting shake training...")
            elif key == ord('t') and self.mode == "menu":
                self.mode = "test"
                self.pitch_hist.clear()
                self.yaw_hist.clear()
                print("🧪 Starting gesture test...")
            elif key == 27:  # ESC
                if self.mode != "menu":
                    self.mode = "menu"
                    print("↩️  Returned to menu")
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("👋 Gesture trainer closed")

if __name__ == "__main__":
    trainer = GestureTrainer()
    trainer.run()