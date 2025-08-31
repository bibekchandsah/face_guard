import os
import json
import time
import math
import threading
from collections import deque

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2
import numpy as np

# --- Optional robust user recognition (preferred) ---
try:
    import face_recognition  # dlib-based encodings
    HAS_FACE_REC = True
except Exception:
    HAS_FACE_REC = False

import mediapipe as mp
import screen_brightness_control as sbc

# GUI & notifications
from PySide6.QtCore import Qt, QTimer, QSize, Signal, QObject, QThread
from PySide6.QtGui import QIcon, QAction, QKeySequence, QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu,
    QTextEdit, QMainWindow, QDockWidget, QHBoxLayout, QPushButton
)

# Global hotkeys
import keyboard

# Use current script directory instead of user home
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(SCRIPT_DIR, "face_guard_data")
UNKNOWN_FACES_DIR = os.path.join(SCRIPT_DIR, "unknown_faces")
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")

# Create directories
os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(UNKNOWN_FACES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

ENCODING_PATH = os.path.join(APP_DIR, "user_face_encoding.json")
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")
LOG_FILE_PATH = os.path.join(LOGS_DIR, f"face_guard_{time.strftime('%Y%m%d')}.log")

# ------------------------ Utility ------------------------

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def cosine_similarity(a, b, eps=1e-8):
    a = np.array(a); b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + eps))

# ---------------------- Logging Bus ----------------------

class LogBus(QObject):
    line = Signal(str)

LOG = LogBus()

def log(msg: str):
    stamp = time.strftime("%H:%M:%S")
    full_stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{stamp}] {msg}"
    
    # Emit to GUI
    LOG.line.emit(log_message)
    
    # Write to file
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{full_stamp}] {msg}\n")
    except Exception:
        pass  # Don't let logging errors crash the app

# ------------------- Toast Notification ------------------

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

class Toast(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel("")
        self.label.setStyleSheet("""
            QLabel {
                background: rgba(30,30,30,0.88);
                color: white; padding: 10px 14px; border-radius: 12px;
                font-size: 13px;
            }
        """)
        lay = QVBoxLayout(self)
        lay.addWidget(self.label)
        lay.setContentsMargins(8,8,8,8)
        self.resize(self.label.sizeHint())
        self.duration_ms = 1800

        # Small status icon (green for nod, red for shake)
        self.icon = QLabel("")
        self.icon.setFixedSize(12,12)
        self.icon.setStyleSheet("border-radius: 6px; background: transparent;")
        lay.addWidget(self.icon, alignment=Qt.AlignRight)

        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)
        self.timer.setSingleShot(True)

    def show_toast(self, text, color=None):
        # Use QTimer.singleShot to ensure thread safety
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._show_toast_impl(text, color))
    
    def _show_toast_impl(self, text, color):
        self.label.setText(text)
        if color == "green":
            self.icon.setStyleSheet("border-radius: 6px; background: #22c55e;")
        elif color == "red":
            self.icon.setStyleSheet("border-radius: 6px; background: #ef4444;")
        else:
            self.icon.setStyleSheet("border-radius: 6px; background: transparent;")

        # Position top-right of screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        self.move(screen.right() - self.width() - 24, screen.top() + 24)
        self.show()
        self.timer.start(self.duration_ms)

# ------------------- Logs Window (on demand) -------------------

class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceGuard • Logs")
        self.setMinimumSize(560, 360)
        # Remove Qt.Tool flag to show in taskbar
        self.setWindowFlags(Qt.Window)
        
        # Set window icon
        icon_path = os.path.join(SCRIPT_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                border: 1px solid #333;
            }
        """)

        # Set as central widget instead of dock
        self.setCentralWidget(self.text)
        LOG.line.connect(self.append)

    def append(self, s: str):
        self.text.append(s)
        # Auto-scroll to bottom
        scrollbar = self.text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

# ------------------- Camera Preview Thread -------------------

class CameraPreviewThread(QThread):
    frame_ready = Signal(np.ndarray, bool, list)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.worker_ref = None
        self.performance_mode = True  # Start in performance mode for better performance
        self.last_update_time = 0
        self.update_interval = 0.1  # 10 FPS for smooth performance
        
    def set_worker(self, worker):
        self.worker_ref = worker
        
    def set_performance_mode(self, enabled):
        self.performance_mode = enabled
        # Adjust update rate based on performance mode
        self.update_interval = 0.1 if enabled else 0.067  # 10 FPS vs 15 FPS
        
    def start_preview(self):
        if not self.running:
            self.running = True
            self.start()
        
    def stop_preview(self):
        if self.running:
            self.running = False
            self.quit()
            self.wait()
    
    def detect_faces_in_frame(self, frame):
        """Fast face detection for preview with smooth green borders"""
        try:
            if not self.worker_ref or not self.worker_ref.owner_encoding:
                return False, []
            
            # Use the main worker's face detection method for consistency
            return self.worker_ref.is_owner_face(frame)
        except Exception:
            return False, []
    
    def run(self):
        while self.running:
            current_time = time.time()
            
            # Throttle updates based on performance mode
            if current_time - self.last_update_time < self.update_interval:
                self.msleep(10)  # Use Qt's msleep for better thread performance
                continue
                
            self.last_update_time = current_time
            
            try:
                # Get shared data from main worker (minimal processing)
                if (self.worker_ref and 
                    hasattr(self.worker_ref, 'current_frame') and 
                    self.worker_ref.current_frame is not None):
                    
                    # Get detection data from main worker (already processed)
                    owner_detected = getattr(self.worker_ref, 'owner_present', False)
                    face_boxes = getattr(self.worker_ref, 'face_boxes', [])
                    
                    # Only flip frame (much faster than copy + flip)
                    frame = cv2.flip(self.worker_ref.current_frame, 1)
                    
                    # Emit frame for display
                    self.frame_ready.emit(frame, owner_detected, face_boxes)
                else:
                    self.msleep(20)  # Wait longer if no frame available
                
            except Exception:
                self.msleep(50)  # Handle errors gracefully

# ------------------- Camera Preview Window -------------------

class CameraPreview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceGuard • Camera Preview")
        self.setMinimumSize(480, 360)
        # Remove Qt.Tool flag to show in taskbar
        self.setWindowFlags(Qt.Window)
        
        # Set window icon
        icon_path = os.path.join(SCRIPT_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #2b2b2b;")
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Camera display
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setStyleSheet("border: 2px solid #555; background: black; border-radius: 5px;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setText("Camera Preview Loading...")
        layout.addWidget(self.camera_label)
        
        # Status info with black background
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px; 
                background-color: #1e1e1e; 
                color: #ffffff; 
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #555;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Control buttons with dark theme
        button_style = """
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666;
                padding: 8px 12px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #888;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
            }
        """
        
        button_layout1 = QHBoxLayout()
        self.toggle_btn = QPushButton("Hide Preview")
        self.reset_face_btn = QPushButton("Reset Owner Face")
        self.performance_btn = QPushButton("Performance Mode: ON")
        
        # Apply dark theme to buttons
        for btn in [self.toggle_btn, self.reset_face_btn, self.performance_btn]:
            btn.setStyleSheet(button_style)
        
        button_layout1.addWidget(self.toggle_btn)
        button_layout1.addWidget(self.reset_face_btn)
        button_layout1.addWidget(self.performance_btn)
        layout.addLayout(button_layout1)
        
        button_layout2 = QHBoxLayout()
        self.test_nod_btn = QPushButton("Test Nod")
        self.test_shake_btn = QPushButton("Test Shake")
        self.view_unknown_btn = QPushButton("View Unknown Faces")
        
        # Apply dark theme to buttons
        for btn in [self.test_nod_btn, self.test_shake_btn, self.view_unknown_btn]:
            btn.setStyleSheet(button_style)
        
        button_layout2.addWidget(self.test_nod_btn)
        button_layout2.addWidget(self.test_shake_btn)
        button_layout2.addWidget(self.view_unknown_btn)
        layout.addLayout(button_layout2)
        
        # Gesture training buttons with special colors
        button_layout3 = QHBoxLayout()
        self.train_nod_btn = QPushButton("🎯 Train Nod Gesture")
        self.train_shake_btn = QPushButton("🎯 Train Shake Gesture")
        self.calibrate_btn = QPushButton("🔧 Calibrate Gestures")
        
        # Special styling for training buttons
        self.train_nod_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: 1px solid #45a049;
                padding: 8px 12px;
                border-radius: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
        """)
        
        self.train_shake_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border: 1px solid #1976D2;
                padding: 8px 12px;
                border-radius: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
        """)
        
        self.calibrate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                border: 1px solid #F57C00;
                padding: 8px 12px;
                border-radius: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
        """)
        
        button_layout3.addWidget(self.train_nod_btn)
        button_layout3.addWidget(self.train_shake_btn)
        button_layout3.addWidget(self.calibrate_btn)
        layout.addLayout(button_layout3)
        
        # Face Recognition Sensitivity Controls
        sensitivity_layout = QHBoxLayout()
        
        # Sensitivity label and slider
        sensitivity_label = QLabel("Face Recognition Sensitivity:")
        sensitivity_label.setStyleSheet("color: #ffffff; font-weight: bold; padding: 5px;")
        
        from PySide6.QtWidgets import QSlider, QSpinBox
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(50)  # 50% minimum
        self.sensitivity_slider.setMaximum(95)  # 95% maximum
        self.sensitivity_slider.setValue(75)    # 75% default
        self.sensitivity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #666;
                height: 8px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #45a049;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #45a049;
            }
        """)
        
        self.sensitivity_spinbox = QSpinBox()
        self.sensitivity_spinbox.setMinimum(50)
        self.sensitivity_spinbox.setMaximum(95)
        self.sensitivity_spinbox.setValue(75)
        self.sensitivity_spinbox.setSuffix("%")
        self.sensitivity_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        
        # Connect slider and spinbox
        self.sensitivity_slider.valueChanged.connect(self.sensitivity_spinbox.setValue)
        self.sensitivity_spinbox.valueChanged.connect(self.sensitivity_slider.setValue)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity)
        
        sensitivity_layout.addWidget(sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        sensitivity_layout.addWidget(self.sensitivity_spinbox)
        layout.addLayout(sensitivity_layout)
        
        # Connect buttons
        self.toggle_btn.clicked.connect(self.hide)
        self.reset_face_btn.clicked.connect(self.reset_owner_face)
        self.performance_btn.clicked.connect(self.toggle_performance_mode)
        self.test_nod_btn.clicked.connect(self.test_nod_gesture)
        self.test_shake_btn.clicked.connect(self.test_shake_gesture)
        self.view_unknown_btn.clicked.connect(self.view_unknown_faces)
        self.train_nod_btn.clicked.connect(self.train_nod_gesture)
        self.train_shake_btn.clicked.connect(self.train_shake_gesture)
        self.calibrate_btn.clicked.connect(self.calibrate_gestures)
        
        # Reference to worker (will be set by main app)
        self.worker = None
        
        # Performance settings
        self.performance_mode = True  # Start in performance mode
        
        # Camera preview thread - initialize with worker reference
        self.preview_thread = None
        
        # Current frame data
        self.current_frame = None
        self.owner_detected = False
        self.face_boxes = []
        
    def set_worker(self, worker):
        """Set the worker reference and initialize preview thread"""
        self.worker = worker
        if self.preview_thread:
            self.preview_thread.stop_preview()
        
        # Create new optimized preview thread
        self.preview_thread = CameraPreviewThread()
        self.preview_thread.set_worker(worker)
        self.preview_thread.frame_ready.connect(self.update_frame_display)
        self.preview_thread.set_performance_mode(self.performance_mode)
        
    def showEvent(self, event):
        """Start camera preview when window is shown"""
        super().showEvent(event)
        if self.preview_thread:
            self.preview_thread.start_preview()
            self.camera_label.setText("Starting camera preview...")
        else:
            self.camera_label.setText("Camera preview not available")
    
    def hideEvent(self, event):
        """Stop camera preview when window is hidden - but keep monitoring active"""
        super().hideEvent(event)
        if self.preview_thread:
            self.preview_thread.stop_preview()
        # NOTE: Main monitoring continues in VisionWorker thread
    
    def closeEvent(self, event):
        """Clean up when window is closed"""
        self.preview_thread.stop_preview()
        super().closeEvent(event)
    
    def toggle_performance_mode(self):
        """Toggle performance mode and sync with preview thread"""
        self.performance_mode = not self.performance_mode
        mode_text = "ON" if self.performance_mode else "OFF"
        self.performance_btn.setText(f"Performance Mode: {mode_text}")
        
        # Sync with preview thread for smooth performance
        if self.preview_thread:
            self.preview_thread.set_performance_mode(self.performance_mode)
        
        log(f"📊 Performance mode: {mode_text} (Preview FPS: {15 if self.performance_mode else 30})")
    
    def reset_owner_face(self):
        """Reset the owner face encoding"""
        try:
            # First reset the worker's encoding to prevent race conditions
            if self.worker:
                self.worker.owner_encoding = None
                log("Worker encoding reset to None")
            
            # Then remove the file
            if os.path.exists(ENCODING_PATH):
                os.remove(ENCODING_PATH)
                log("Owner face file deleted")
            
            log("Owner face data reset. Please re-register your face.")
            self.status_label.setText("Status: Owner face reset - Please look at camera to re-register")
            
            # Show toast notification
            if hasattr(self, 'worker') and self.worker and hasattr(self.worker, 'on_toast'):
                self.worker.on_toast("Owner face reset - Please look at camera", "red")
                
        except Exception as e:
            log(f"Failed to reset owner face: {e}")
            self.status_label.setText(f"Status: Reset failed - {e}")
    
    def test_nod_gesture(self):
        """Test nod gesture detection"""
        if self.worker:
            log("Testing nod gesture - Please nod your head up and down twice")
            self.worker.start_gesture_test("nod")
            self.status_label.setText("Status: Testing nod gesture - Nod up and down twice")
    
    def test_shake_gesture(self):
        """Test shake gesture detection"""
        if self.worker:
            log("Testing shake gesture - Please shake your head left and right twice")
            self.worker.start_gesture_test("shake")
            self.status_label.setText("Status: Testing shake gesture - Shake left and right twice")
    
    def train_nod_gesture(self):
        """Train nod gesture by recording user's movements"""
        if self.worker:
            log("🎯 Training nod gesture - Please nod your head up and down 5 times slowly")
            self.worker.start_gesture_training("nod")
            self.status_label.setText("Status: 🎯 TRAINING NOD - Nod up and down 5 times slowly")
            self.train_nod_btn.setText("🔴 Recording Nod...")
            self.train_nod_btn.setEnabled(False)
    
    def train_shake_gesture(self):
        """Train shake gesture by recording user's movements"""
        if self.worker:
            log("🎯 Training shake gesture - Please shake your head left and right 5 times slowly")
            self.worker.start_gesture_training("shake")
            self.status_label.setText("Status: 🎯 TRAINING SHAKE - Shake left and right 5 times slowly")
            self.train_shake_btn.setText("🔴 Recording Shake...")
            self.train_shake_btn.setEnabled(False)
    
    def calibrate_gestures(self):
        """Calibrate gesture detection thresholds"""
        if self.worker:
            log("🔧 Calibrating gestures - Look straight at camera for 3 seconds")
            self.worker.start_gesture_calibration()
            self.status_label.setText("Status: 🔧 CALIBRATING - Look straight at camera, don't move")
            self.calibrate_btn.setText("🔴 Calibrating...")
            self.calibrate_btn.setEnabled(False)
    
    def on_training_complete(self, gesture_type, success):
        """Called when gesture training is complete"""
        if gesture_type == "nod":
            self.train_nod_btn.setText("🎯 Train Nod Gesture")
            self.train_nod_btn.setEnabled(True)
            if success:
                self.status_label.setText("Status: ✅ Nod training completed successfully!")
            else:
                self.status_label.setText("Status: ❌ Nod training failed - try again")
        elif gesture_type == "shake":
            self.train_shake_btn.setText("🎯 Train Shake Gesture")
            self.train_shake_btn.setEnabled(True)
            if success:
                self.status_label.setText("Status: ✅ Shake training completed successfully!")
            else:
                self.status_label.setText("Status: ❌ Shake training failed - try again")
        elif gesture_type == "calibrate":
            self.calibrate_btn.setText("🔧 Calibrate Gestures")
            self.calibrate_btn.setEnabled(True)
            if success:
                self.status_label.setText("Status: ✅ Gesture calibration completed!")
            else:
                self.status_label.setText("Status: ❌ Calibration failed - try again")
    
    def update_sensitivity(self, value):
        """Update face recognition sensitivity"""
        if self.worker:
            # Convert percentage to face_recognition tolerance (inverse relationship)
            # Higher percentage = lower tolerance = more strict
            # 75% = 0.48 tolerance, 50% = 0.6 tolerance, 95% = 0.3 tolerance
            tolerance = 0.8 - (value / 100.0) * 0.5  # Maps 50-95% to 0.55-0.325 tolerance
            self.worker.face_recognition_tolerance = tolerance
            log(f"Face recognition sensitivity set to {value}% (tolerance: {tolerance:.3f})")
            self.status_label.setText(f"Status: Face recognition sensitivity: {value}%")
    
    def view_unknown_faces(self):
        """Open folder containing unknown face images"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", UNKNOWN_FACES_DIR])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", UNKNOWN_FACES_DIR])
            else:  # Linux
                subprocess.run(["xdg-open", UNKNOWN_FACES_DIR])
            
            log(f"Opened unknown faces folder: {UNKNOWN_FACES_DIR}")
        except Exception as e:
            log(f"Failed to open unknown faces folder: {e}")
    
    def update_frame_display(self, frame, owner_detected, face_boxes):
        """Update the camera preview display with new frame from thread - OPTIMIZED"""
        try:
            # Store current data (no unnecessary copying)
            self.owner_detected = owner_detected
            self.face_boxes = face_boxes
            
            # Skip frame processing if performance mode throttling is active
            if self.performance_mode:
                current_time = time.time()
                if hasattr(self, 'last_display_update'):
                    if current_time - self.last_display_update < 0.1:  # Max 10 FPS
                        return
                self.last_display_update = current_time
            
            # Work directly on the frame (no copying for better performance)
            h, w = frame.shape[:2]
            
            # Draw face detection boxes (simplified for performance)
            for box in face_boxes:
                if len(box) == 4:  # face_recognition format: (top, right, bottom, left)
                    top, right, bottom, left = box
                    # Adjust coordinates for horizontally flipped frame
                    left_flipped = w - right
                    right_flipped = w - left
                    
                    # Simple, efficient borders
                    color = (0, 255, 0) if owner_detected else (0, 0, 255)  # Green or Red
                    cv2.rectangle(frame, (left_flipped, top), (right_flipped, bottom), color, 2)
                    
                    # Simple label
                    label = "OWNER" if owner_detected else "UNKNOWN"
                    cv2.putText(frame, label, (left_flipped, top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add status overlay (simplified)
            status_text = f"Owner: {'PRESENT' if owner_detected else 'NOT DETECTED'}"
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add training/calibration status (get from worker directly)
            if self.worker:
                if getattr(self.worker, 'gesture_training_mode', False):
                    training_type = getattr(self.worker, 'gesture_training_type', 'UNKNOWN').upper()
                    patterns_count = len(getattr(self.worker, 'training_data', {}).get(
                        getattr(self.worker, 'gesture_training_type', 'nod'), []))
                    cv2.putText(frame, f"🎯 TRAINING {training_type} ({patterns_count}/5)", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                elif getattr(self.worker, 'calibration_mode', False):
                    cv2.putText(frame, "🔧 CALIBRATING - Stay Still", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                elif getattr(self.worker, 'gesture_test_mode', False):
                    test_type = getattr(self.worker, 'gesture_test_type', 'UNKNOWN').upper()
                    cv2.putText(frame, f"🧪 TESTING {test_type}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            
            # Add performance mode indicator
            if self.performance_mode:
                cv2.putText(frame, "Performance Mode", (10, h - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Add gesture thresholds info (bottom right)
            if self.worker and hasattr(self.worker, 'nod_threshold'):
                threshold_text = f"Nod: {self.worker.nod_threshold:.1f}° Shake: {self.worker.shake_threshold:.1f}°"
                cv2.putText(frame, threshold_text, (w - 300, h - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            # Optimized Qt conversion (no extra copying)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Fast scaling with less smooth transformation for better performance
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
            self.camera_label.setPixmap(scaled_pixmap)
            
            # Update status
            status = "Owner Present ✅" if owner_detected else "Owner Not Detected ❌"
            perf_status = " (Performance Mode)" if self.performance_mode else ""
            self.status_label.setText(f"Status: {status}{perf_status}")
            
        except Exception as e:
            log(f"Error updating camera display: {e}")

# --------------------- Vision Worker ---------------------

class VisionWorker(threading.Thread):
    """
    Webcam + detection + gesture logic. Emits GUI events via LogBus + callbacks.
    """
    def __init__(self, on_toast, on_unknown_face, on_nod, on_shake, on_brightness_change, camera_preview=None):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DSHOW helps on Windows
        self.running = True

        self.on_toast = on_toast
        self.on_unknown_face = on_unknown_face
        self.on_nod = on_nod
        self.on_shake = on_shake
        self.on_brightness_change = on_brightness_change
        self.camera_preview = camera_preview

        self.owner_encoding = self._load_owner_encoding()

        # MediaPipe Face Mesh for head gesture
        self.mp_face = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        # Gesture detection buffers
        self.pitch_hist = deque(maxlen=30)  # ~1 sec at ~30fps
        self.yaw_hist = deque(maxlen=30)
        self.last_unknown_ts = 0
        self.awaiting_gesture = False
        self.gesture_deadline = 0
        self.gesture_confirmed = False

        # Brightness state
        self.normal_brightness = self._get_current_brightness()
        self.reduced = False
        self.owner_absent_start = None
        self.brightness_dimmed_for_absence = False
        
        # Face detection state
        self.current_frame = None
        self.face_boxes = []
        
        # Face recognition settings
        self.face_recognition_tolerance = 0.48  # Default 75% sensitivity (0.48 tolerance)
        
        # Optimized face detection for real-time preview
        if HAS_FACE_REC:
            import face_recognition
            self.face_rec = face_recognition
        self.owner_present = False
        
        # Unknown face logging
        self.last_unknown_save = 0
        self.unknown_face_counter = 0
        
        # Gesture testing
        self.gesture_test_mode = False
        self.gesture_test_type = None
        self.gesture_test_start = None
        
        # Gesture training
        self.gesture_training_mode = False
        self.gesture_training_type = None
        self.gesture_training_start = None
        self.training_data = {"nod": [], "shake": []}
        self.calibration_mode = False
        self.calibration_start = None
        self.baseline_pitch = 0.0
        self.baseline_yaw = 0.0
        
        # Load saved gesture patterns
        self.gesture_patterns = self._load_gesture_patterns()
        
        # Adaptive thresholds
        self.nod_threshold = 12.0
        self.shake_threshold = 15.0

    # ---------- Face registration & matching ----------

    def _load_owner_encoding(self):
        data = load_json(ENCODING_PATH)
        if data and "encoding" in data and HAS_FACE_REC:
            log("Loaded saved owner face encoding.")
            return np.array(data["encoding"], dtype=np.float32)
        elif data and "landmark_embedding" in data and not HAS_FACE_REC:
            log("Loaded saved owner landmark embedding (fallback mode).")
            return np.array(data["landmark_embedding"], dtype=np.float32)
        return None

    def _save_owner_encoding(self, encoding):
        if HAS_FACE_REC:
            save_json(ENCODING_PATH, {"encoding": encoding.tolist()})
            log("Owner face encoding saved.")
        else:
            save_json(ENCODING_PATH, {"landmark_embedding": encoding.tolist()})
            log("Owner landmark embedding saved (fallback).")

    def register_owner_if_needed(self, frame_bgr):
        if self.owner_encoding is not None:
            return

        log("No owner face registered. Please face the camera...")
        self.on_toast("Registering your face...", None)

        if HAS_FACE_REC:
            # Capture multiple frames & average encoding
            encs = []
            start = time.time()
            while time.time() - start < 3.0:
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model="hog")
                if boxes:
                    enc = face_recognition.face_encodings(rgb, boxes)[0]
                    encs.append(enc)
                ret, frame_bgr = self.cap.read()
                if not ret:
                    break
            if encs:
                enc = np.mean(np.array(encs), axis=0)
                self.owner_encoding = enc
                self._save_owner_encoding(enc)
                self.on_toast("Face registered ✅", "green")
                log("Owner face registered (face_recognition).")
        else:
            # Fallback: use mediapipe landmarks (rough)
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            res = self.mp_face.process(rgb)
            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0]
                pts = []
                for p in lm.landmark:
                    pts.append([p.x, p.y, p.z])
                emb = np.array(pts, dtype=np.float32).flatten()
                self.owner_encoding = emb
                self._save_owner_encoding(emb)
                self.on_toast("Face registered ✅ (fallback)", "green")
                log("Owner face registered (landmark embedding fallback).")

    def is_owner_face(self, frame_bgr) -> tuple:
        """Returns (is_owner, face_boxes) tuple"""
        # Thread-safe check for owner encoding
        owner_enc = self.owner_encoding
        if owner_enc is None:
            return False, []

        if HAS_FACE_REC:
            try:
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model="hog")
                if not boxes:
                    return False, []
                encs = face_recognition.face_encodings(rgb, boxes)
                if not encs or len(encs) == 0:
                    return False, boxes
                
                # Additional safety check
                if owner_enc is None or encs[0] is None:
                    return False, boxes
                
                # Compare with configurable tolerance
                distances = face_recognition.face_distance([owner_enc], encs[0])
                if distances is None or len(distances) == 0:
                    return False, boxes
                    
                match = distances[0] < self.face_recognition_tolerance
                return bool(match), boxes
            except Exception as e:
                log(f"Error in face recognition: {e}")
                return False, []
        else:
            # Fallback: cosine similarity between landmark embeddings
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            res = self.mp_face.process(rgb)
            if not res.multi_face_landmarks:
                return False, []
            lm = res.multi_face_landmarks[0]
            pts = []
            for p in lm.landmark:
                pts.append([p.x, p.y, p.z])
            emb = np.array(pts, dtype=np.float32).flatten()
            sim = cosine_similarity(self.owner_encoding, emb)
            
            # Create approximate face box from landmarks
            h, w = frame_bgr.shape[:2]
            x_coords = [p.x * w for p in lm.landmark]
            y_coords = [p.y * h for p in lm.landmark]
            left, right = int(min(x_coords)), int(max(x_coords))
            top, bottom = int(min(y_coords)), int(max(y_coords))
            face_box = [(top, right, bottom, left)]
            
            return sim > 0.995, face_box  # tight threshold; adjust if needed

    # ---------- Brightness helpers ----------

    def _get_current_brightness(self):
        try:
            return sbc.get_brightness(display=0)
        except Exception:
            return 100

    def set_brightness(self, val):
        val = int(max(0, min(100, val)))
        try:
            sbc.set_brightness(val)
            self.on_brightness_change(val)
            log(f"Brightness set to {val}%.")
        except Exception as e:
            log(f"Brightness change failed: {e}")

    def restore_brightness(self):
        self.set_brightness(self.normal_brightness if isinstance(self.normal_brightness, int) else 100)
        self.reduced = False
    
    # ---------- Unknown face logging ----------
    
    def save_unknown_face(self, frame, face_boxes):
        """Save unknown face image to folder"""
        try:
            now = time.time()
            # Only save once every 5 seconds to avoid spam
            if now - self.last_unknown_save < 5.0:
                return
                
            self.last_unknown_save = now
            self.unknown_face_counter += 1
            
            # Create filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"unknown_face_{timestamp}_{self.unknown_face_counter:03d}.jpg"
            filepath = os.path.join(UNKNOWN_FACES_DIR, filename)
            
            # Draw face boxes on the image
            frame_with_boxes = frame.copy()
            for box in face_boxes:
                if len(box) == 4:
                    top, right, bottom, left = box
                    cv2.rectangle(frame_with_boxes, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame_with_boxes, "UNKNOWN", (left, top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Add timestamp overlay
            cv2.putText(frame_with_boxes, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Save the image
            cv2.imwrite(filepath, frame_with_boxes)
            log(f"Unknown face saved: {filename}")
            
        except Exception as e:
            log(f"Failed to save unknown face: {e}")
    
    # ---------- Gesture testing ----------
    
    def _load_gesture_patterns(self):
        """Load saved gesture patterns from file"""
        patterns_path = os.path.join(APP_DIR, "gesture_patterns.json")
        return load_json(patterns_path, {"nod": [], "shake": []})
    
    def _save_gesture_patterns(self):
        """Save gesture patterns to file"""
        patterns_path = os.path.join(APP_DIR, "gesture_patterns.json")
        save_json(patterns_path, self.gesture_patterns)
        log("Gesture patterns saved")
    
    def start_gesture_training(self, gesture_type):
        """Start gesture training mode"""
        self.gesture_training_mode = True
        self.gesture_training_type = gesture_type
        self.gesture_training_start = time.time()
        self.pitch_hist.clear()
        self.yaw_hist.clear()
        self.training_data[gesture_type] = []
        log(f"🎯 Started {gesture_type} gesture training - Record 5 clear movements")
    
    def start_gesture_calibration(self):
        """Start gesture calibration mode"""
        self.calibration_mode = True
        self.calibration_start = time.time()
        self.pitch_hist.clear()
        self.yaw_hist.clear()
        log("🔧 Started gesture calibration - establishing baseline")
    
    def start_gesture_test(self, gesture_type):
        """Start gesture testing mode"""
        self.gesture_test_mode = True
        self.gesture_test_type = gesture_type
        self.gesture_test_start = time.time()
        self.pitch_hist.clear()
        self.yaw_hist.clear()
        log(f"Started {gesture_type} gesture test - You have 10 seconds")
    
    def check_gesture_training(self):
        """Check and process gesture training"""
        if not self.gesture_training_mode:
            return
            
        now = time.time()
        elapsed = now - self.gesture_training_start
        
        # Training timeout after 15 seconds
        if elapsed > 15.0:
            self.gesture_training_mode = False
            log(f"❌ {self.gesture_training_type} training timed out")
            self.on_toast(f"{self.gesture_training_type.title()} training timed out", "red")
            if self.camera_preview:
                self.camera_preview.on_training_complete(self.gesture_training_type, False)
            return
        
        # Collect training data
        if len(self.pitch_hist) > 0 and len(self.yaw_hist) > 0:
            if self.gesture_training_type == "nod":
                # Record pitch movements for nod training
                pitch_range = max(self.pitch_hist) - min(self.pitch_hist)
                if pitch_range > 5.0:  # Significant movement detected
                    pattern = {
                        "pitch_data": list(self.pitch_hist),
                        "yaw_data": list(self.yaw_hist),
                        "pitch_range": pitch_range,
                        "timestamp": now
                    }
                    self.training_data["nod"].append(pattern)
                    log(f"📊 Recorded nod pattern {len(self.training_data['nod'])}/5 (range: {pitch_range:.1f}°)")
                    
            elif self.gesture_training_type == "shake":
                # Record yaw movements for shake training
                yaw_range = max(self.yaw_hist) - min(self.yaw_hist)
                if yaw_range > 5.0:  # Significant movement detected
                    pattern = {
                        "pitch_data": list(self.pitch_hist),
                        "yaw_data": list(self.yaw_hist),
                        "yaw_range": yaw_range,
                        "timestamp": now
                    }
                    self.training_data["shake"].append(pattern)
                    log(f"📊 Recorded shake pattern {len(self.training_data['shake'])}/5 (range: {yaw_range:.1f}°)")
        
        # Check if we have enough training data
        if len(self.training_data[self.gesture_training_type]) >= 5:
            self._complete_gesture_training()
    
    def _complete_gesture_training(self):
        """Complete gesture training and update thresholds"""
        gesture_type = self.gesture_training_type
        patterns = self.training_data[gesture_type]
        
        if len(patterns) >= 3:  # Need at least 3 good patterns
            # Analyze patterns and set adaptive thresholds
            if gesture_type == "nod":
                ranges = [p["pitch_range"] for p in patterns]
                avg_range = sum(ranges) / len(ranges)
                self.nod_threshold = max(8.0, avg_range * 0.6)  # 60% of average range
                log(f"✅ Nod training complete! New threshold: {self.nod_threshold:.1f}°")
                
            elif gesture_type == "shake":
                ranges = [p["yaw_range"] for p in patterns]
                avg_range = sum(ranges) / len(ranges)
                self.shake_threshold = max(10.0, avg_range * 0.6)  # 60% of average range
                log(f"✅ Shake training complete! New threshold: {self.shake_threshold:.1f}°")
            
            # Save patterns
            self.gesture_patterns[gesture_type] = patterns[-3:]  # Keep last 3 patterns
            self._save_gesture_patterns()
            
            self.on_toast(f"✅ {gesture_type.title()} training complete!", "green")
            success = True
        else:
            log(f"❌ {gesture_type} training failed - not enough clear patterns")
            self.on_toast(f"❌ {gesture_type.title()} training failed", "red")
            success = False
        
        self.gesture_training_mode = False
        if self.camera_preview:
            self.camera_preview.on_training_complete(gesture_type, success)
    
    def check_gesture_calibration(self):
        """Check and process gesture calibration"""
        if not self.calibration_mode:
            return
            
        now = time.time()
        elapsed = now - self.calibration_start
        
        if elapsed > 3.0:  # 3 second calibration
            if len(self.pitch_hist) > 10 and len(self.yaw_hist) > 10:
                # Calculate baseline (neutral position)
                self.baseline_pitch = sum(self.pitch_hist) / len(self.pitch_hist)
                self.baseline_yaw = sum(self.yaw_hist) / len(self.yaw_hist)
                
                log(f"✅ Calibration complete! Baseline - Pitch: {self.baseline_pitch:.1f}°, Yaw: {self.baseline_yaw:.1f}°")
                self.on_toast("✅ Calibration complete!", "green")
                success = True
            else:
                log("❌ Calibration failed - insufficient data")
                self.on_toast("❌ Calibration failed", "red")
                success = False
            
            self.calibration_mode = False
            if self.camera_preview:
                self.camera_preview.on_training_complete("calibrate", success)
    
    def check_gesture_test(self):
        """Check gesture test results"""
        if not self.gesture_test_mode:
            return
            
        now = time.time()
        if now - self.gesture_test_start > 10.0:  # 10 second timeout
            self.gesture_test_mode = False
            log("Gesture test timed out")
            self.on_toast("Gesture test timed out", "red")
            return
        
        is_nod, is_shake = self._detect_gesture()
        
        if self.gesture_test_type == "nod" and is_nod:
            self.gesture_test_mode = False
            log("✅ Nod gesture test PASSED!")
            self.on_toast("Nod gesture test PASSED! ✅", "green")
        elif self.gesture_test_type == "shake" and is_shake:
            self.gesture_test_mode = False
            log("✅ Shake gesture test PASSED!")
            self.on_toast("Shake gesture test PASSED! ✅", "green")
        elif self.gesture_test_type == "nod" and is_shake:
            self.gesture_test_mode = False
            log("❌ Nod test failed - detected shake instead")
            self.on_toast("Nod test failed - detected shake instead", "red")
        elif self.gesture_test_type == "shake" and is_nod:
            self.gesture_test_mode = False
            log("❌ Shake test failed - detected nod instead")
            self.on_toast("Shake test failed - detected nod instead", "red")

    # ---------- Gesture detection ----------

    def _estimate_head_angles(self, frame_bgr):
        """
        Returns (pitch, yaw) in degrees using FaceMesh landmarks.
        Uses both pose estimation and fallback landmark-based method.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.mp_face.process(rgb)
        if not res.multi_face_landmarks:
            return None, None

        lm = res.multi_face_landmarks[0].landmark
        h, w = frame_bgr.shape[:2]

        # Try pose estimation first
        try:
            # Use 6 landmark points for proper pose estimation (OpenCV requires at least 6)
            idxs = [1, 33, 263, 61, 291, 10]  # nose tip, left eye outer, right eye outer, mouth left/right, chin
            pts2d = np.array([(lm[i].x * w, lm[i].y * h) for i in idxs], dtype=np.float32)

            # Corresponding 3D model points (arbitrary units)
            pts3d = np.array([
                [0.0, 0.0, 0.0],        # nose tip
                [-30.0, -30.0, -30.0],  # left eye outer
                [30.0, -30.0, -30.0],   # right eye outer
                [-25.0, 30.0, -20.0],   # mouth left
                [25.0, 30.0, -20.0],    # mouth right
                [0.0, 50.0, -10.0],     # chin
            ], dtype=np.float32)

            cam_matrix = np.array([[w, 0, w/2],
                                   [0, w, h/2],
                                   [0, 0, 1]], dtype=np.float32)
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
            pass  # Fall through to simple method
        
        # Fallback: Simple landmark-based estimation
        try:
            # Use nose tip (1) and forehead (10) for pitch
            nose_y = lm[1].y
            forehead_y = lm[10].y
            pitch = (nose_y - forehead_y) * 180  # Rough pitch estimate
            
            # Use nose tip and face center for yaw
            face_center_x = (lm[33].x + lm[263].x) / 2  # Average of eye corners
            nose_x = lm[1].x
            yaw = (nose_x - face_center_x) * 180  # Rough yaw estimate
            
            return pitch, yaw
        except Exception:
            return None, None

    def _detect_gesture(self):
        """
        Improved gesture detection using adaptive thresholds and baseline correction.
        """
        if len(self.pitch_hist) < 10 or len(self.yaw_hist) < 10:
            return False, False
        
        # Apply baseline correction
        corrected_pitch = [p - self.baseline_pitch for p in self.pitch_hist]
        corrected_yaw = [y - self.baseline_yaw for y in self.yaw_hist]
        
        # Use adaptive thresholds
        pitch_threshold = self.nod_threshold
        yaw_threshold = self.shake_threshold

        # Count sign changes beyond threshold
        def count_oscillations(seq, th):
            # Convert to +1 / -1 / 0 states based on threshold
            states = []
            for v in seq:
                if v > th:
                    states.append(1)
                elif v < -th:
                    states.append(-1)
                else:
                    states.append(0)
            
            # Count transitions between +1 and -1 (complete oscillations)
            count = 0
            last_nonzero = 0
            for s in states:
                if s != 0 and s != last_nonzero and last_nonzero != 0:
                    count += 1
                if s != 0:
                    last_nonzero = s
            return count

        # Detect gestures
        pitch_oscillations = count_oscillations(corrected_pitch, pitch_threshold)
        yaw_oscillations = count_oscillations(corrected_yaw, yaw_threshold)
        
        # Require at least 2 oscillations for gesture detection
        is_nod = pitch_oscillations >= 2 and yaw_oscillations < 2
        is_shake = yaw_oscillations >= 2 and pitch_oscillations < 2
        
        # Debug logging during training/testing
        if self.gesture_training_mode or self.gesture_test_mode:
            log(f"Gesture analysis - Pitch osc: {pitch_oscillations}, Yaw osc: {yaw_oscillations}, "
                f"Thresholds - Nod: {pitch_threshold:.1f}°, Shake: {yaw_threshold:.1f}°")
        
        return is_nod, is_shake

    # ---------- Main loop ----------

    def run(self):
        if not self.cap.isOpened():
            log("ERROR: Cannot open webcam.")
            return

        # Attempt first frame to register owner if needed
        ret, frame = self.cap.read()
        if ret:
            self.register_owner_if_needed(frame)

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.02)
                continue

            # Store current frame (original orientation for processing)
            self.current_frame = frame.copy()

            # Register (if user deleted the file mid-run)
            if self.owner_encoding is None:
                self.register_owner_if_needed(frame)
                # Camera preview handled by separate thread
                continue

            # Check if owner in frame
            owner_here, face_boxes = self.is_owner_face(frame)
            self.face_boxes = face_boxes
            self.owner_present = owner_here

            # Camera preview is handled by separate thread - no updates needed here
            # This ensures main monitoring continues even when preview is closed

            pitch, yaw = self._estimate_head_angles(frame)
            if pitch is not None:
                self.pitch_hist.append(pitch)
                self.yaw_hist.append(yaw)

            now = time.time()
            
            # Check gesture test if active
            if self.gesture_test_mode:
                self.check_gesture_test()
            
            # Check gesture training if active
            if self.gesture_training_mode:
                self.check_gesture_training()
            
            # Check gesture calibration if active
            if self.calibration_mode:
                self.check_gesture_calibration()

            # Owner presence-based brightness control
            if owner_here:
                # Owner is present
                if self.owner_absent_start is not None:
                    # Owner just returned
                    log("Owner returned → restoring brightness")
                    self.restore_brightness()
                    self.brightness_dimmed_for_absence = False
                    self.owner_absent_start = None
                    self.on_toast("Owner detected — Brightness restored", "green")
            else:
                # Owner is not present
                if self.owner_absent_start is None:
                    # Owner just left
                    self.owner_absent_start = now
                    log("Owner left camera view")
                elif not self.brightness_dimmed_for_absence and (now - self.owner_absent_start) > 3.0:
                    # Owner has been absent for 3 seconds, dim brightness to 0
                    log("Owner absent for 3 seconds → dimming brightness to 0%")
                    self.set_brightness(0)
                    self.brightness_dimmed_for_absence = True
                    self.on_toast("Owner absent — Brightness dimmed to 0%", "red")

            # Unknown face handling (only if there are faces but owner is not present)
            if face_boxes and not owner_here:
                # Save unknown face image
                self.save_unknown_face(frame, face_boxes)
                
                # Only trigger gesture confirmation if we weren't already waiting
                if not self.awaiting_gesture and not self.gesture_test_mode and (now - self.last_unknown_ts) > 2.0:
                    self.last_unknown_ts = now
                    self.awaiting_gesture = True
                    self.gesture_deadline = now + 6.0  # 6 seconds to confirm
                    log("Unknown face detected → awaiting gesture confirmation.")
                    self.on_unknown_face()
                    self.on_toast("Unknown face detected — Nod twice to dim, Shake to cancel", None)

            # If awaiting gesture, evaluate nod/shake (but not during gesture test)
            if self.awaiting_gesture and not self.gesture_test_mode:
                is_nod, is_shake = self._detect_gesture()
                if is_nod:
                    self.awaiting_gesture = False
                    self.gesture_confirmed = True
                    self.on_nod()
                    self.on_toast("Nod detected — Dimming to 25%", "green")
                    self.set_brightness(25)
                    self.reduced = True
                elif is_shake:
                    self.awaiting_gesture = False
                    self.gesture_confirmed = False
                    self.on_shake()
                    self.on_toast("Shake detected — Cancelled", "red")

                # Timeout without gesture → cancel
                if now > self.gesture_deadline and self.awaiting_gesture:
                    self.awaiting_gesture = False
                    log("Gesture confirmation timed out — Cancelled.")
                    self.on_toast("Timeout — Cancelled", "red")

            time.sleep(0.01)

        self.cap.release()

# ---------------------- Main Application ----------------------

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        # Create system tray icon
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("FaceGuard - Face Detection & Brightness Control")
        
        # Try to use icon.png, fallback to generated icon
        icon_path = os.path.join(SCRIPT_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
            log(f"Using custom icon: {icon_path}")
        else:
            # Create a simple fallback icon
            from PySide6.QtGui import QPixmap, QPainter, QBrush
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(Qt.blue))
            painter.drawEllipse(2, 2, 12, 12)
            painter.end()
            self.tray.setIcon(QIcon(pixmap))
            log("Using fallback generated icon (icon.png not found)")
        self.menu = QMenu()

        self.action_show_logs = QAction("📋 Show Logs")
        self.action_show_camera = QAction("�t Show Camera Preview")
        self.action_restore = QAction("💡 Restore Brightness")
        self.action_status = QAction("ℹ️ Status")
        self.action_exit = QAction("❌ Exit")
        
        self.menu.addAction(self.action_status)
        self.menu.addSeparator()
        self.menu.addAction(self.action_show_logs)
        self.menu.addAction(self.action_show_camera)
        self.menu.addAction(self.action_restore)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)

        self.tray.setContextMenu(self.menu)
        self.tray.show()

        self.toast = Toast()
        self.logs = LogWindow()
        self.camera_preview = CameraPreview()

        self.action_show_logs.triggered.connect(self.logs.show)
        self.action_show_camera.triggered.connect(self.camera_preview.show)
        self.action_restore.triggered.connect(self.restore_brightness)
        self.action_status.triggered.connect(self.show_status)
        self.action_exit.triggered.connect(self.quit_all)
        
        # Add unknown faces viewer action
        self.action_view_unknown = QAction("👤 View Unknown Faces")
        self.action_view_unknown.triggered.connect(self.view_unknown_faces)
        self.menu.insertAction(self.action_restore, self.action_view_unknown)

        # Start worker (main monitoring thread - always runs)
        self.worker = VisionWorker(
            on_toast=self.toast.show_toast,
            on_unknown_face=lambda: log("Event: Unknown face → Ask for gesture."),
            on_nod=lambda: log("Event: Nod detected → Reduce brightness."),
            on_shake=lambda: log("Event: Shake detected → Cancel."),
            on_brightness_change=lambda val: None,
            camera_preview=self.camera_preview
        )
        
        # Connect worker to camera preview with proper threading
        self.camera_preview.set_worker(self.worker)
        
        # Start main monitoring (independent of preview window)
        self.worker.start()
        log("🛡️ Main monitoring thread started (independent of camera preview)")

        # Global hotkeys
        keyboard.add_hotkey("ctrl+shift+r", self.restore_brightness)
        keyboard.add_hotkey("ctrl+shift+l", self.toggle_logs)
        keyboard.add_hotkey("ctrl+shift+c", self.toggle_camera)

        log("App started. Hotkeys: Ctrl+Shift+R (restore brightness), Ctrl+Shift+L (logs), Ctrl+Shift+C (camera).")

    def toggle_logs(self):
        if self.logs.isVisible():
            self.logs.hide()
        else:
            self.logs.show()

    def toggle_camera(self):
        if self.camera_preview.isVisible():
            self.camera_preview.hide()
        else:
            self.camera_preview.show()

    def restore_brightness(self):
        log("Override hotkey pressed → restore brightness.")
        self.worker.restore_brightness()
        self.toast.show_toast("Brightness restored", "green")

    def show_status(self):
        """Show current status in a toast"""
        owner_status = "✅ Registered" if self.worker.owner_encoding is not None else "❌ Not registered"
        brightness_status = f"💡 {self.worker._get_current_brightness()}%"
        gesture_status = "⏳ Waiting for gesture" if self.worker.awaiting_gesture else "👁️ Monitoring"
        
        status_msg = f"Owner: {owner_status} | Brightness: {brightness_status} | Status: {gesture_status}"
        self.toast.show_toast(status_msg, None)
        log(f"Status check: {status_msg}")
    
    def view_unknown_faces(self):
        """Open folder containing unknown face images"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", UNKNOWN_FACES_DIR])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", UNKNOWN_FACES_DIR])
            else:  # Linux
                subprocess.run(["xdg-open", UNKNOWN_FACES_DIR])
            
            log(f"Opened unknown faces folder: {UNKNOWN_FACES_DIR}")
            
            # Count files in the folder
            try:
                file_count = len([f for f in os.listdir(UNKNOWN_FACES_DIR) if f.endswith('.jpg')])
                self.toast.show_toast(f"Unknown faces folder opened ({file_count} images)", None)
            except:
                self.toast.show_toast("Unknown faces folder opened", None)
                
        except Exception as e:
            log(f"Failed to open unknown faces folder: {e}")
            self.toast.show_toast("Failed to open unknown faces folder", "red")

    def quit_all(self):
        log("Exiting FaceGuard...")
        self.worker.running = False
        time.sleep(0.1)
        self.quit()

def main():
    # Log startup information
    print("🛡️  FaceGuard Starting...")
    print(f"📁 Data Directory: {APP_DIR}")
    print(f"📁 Unknown Faces: {UNKNOWN_FACES_DIR}")
    print(f"📁 Logs Directory: {LOGS_DIR}")
    print(f"📄 Log File: {LOG_FILE_PATH}")
    
    app = App([])
    
    # Log startup completion
    log("🛡️ FaceGuard started successfully")
    log(f"📁 Data stored in: {APP_DIR}")
    log(f"📁 Unknown faces in: {UNKNOWN_FACES_DIR}")
    log(f"📄 Logs saved to: {LOG_FILE_PATH}")
    
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
