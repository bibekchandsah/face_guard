#!/usr/bin/env python3
"""
Test toast notifications to verify they work correctly
"""
import sys
import time
from PySide6.QtCore import Qt, QTimer, QApplication
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

# Import the Toast class from face_guard
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simplified Toast class for testing
class TestToast(QWidget):
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

        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)
        self.timer.setSingleShot(True)

    def show_toast(self, text, color=None, duration_ms=5000):
        print(f"Toast called: {text} (color: {color})")
        self.label.setText(text)
        
        # Position top-right of screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        self.move(screen.right() - self.width() - 24, screen.top() + 24)
        self.show()
        
        self.timer.start(duration_ms)
        print(f"Toast displayed for {duration_ms}ms")

def test_toasts():
    app = QApplication(sys.argv)
    
    toast = TestToast()
    
    # Test different toast types
    print("Testing toast notifications...")
    
    # Test 1: Startup notification
    toast.show_toast("🛡️ FaceGuard Active — Monitoring for security", "green")
    QTimer.singleShot(2000, lambda: toast.show_toast("⚠️ Owner left camera view — Screen will dim in 3 seconds", "orange"))
    QTimer.singleShot(4000, lambda: toast.show_toast("🚨 UNKNOWN FACE DETECTED — Nod twice to dim, Shake to cancel", "red"))
    QTimer.singleShot(6000, lambda: app.quit())
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_toasts()