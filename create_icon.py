#!/usr/bin/env python3
"""
Create a simple icon.png for FaceGuard system tray
"""

from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a 32x32 icon
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a shield-like shape for security
    # Outer shield (dark blue)
    shield_points = [
        (16, 2),   # top center
        (28, 8),   # top right
        (28, 20),  # bottom right
        (16, 30),  # bottom center
        (4, 20),   # bottom left
        (4, 8),    # top left
    ]
    draw.polygon(shield_points, fill=(25, 118, 210, 255), outline=(13, 71, 161, 255))
    
    # Inner shield (lighter blue)
    inner_shield = [
        (16, 5),
        (25, 10),
        (25, 19),
        (16, 26),
        (7, 19),
        (7, 10),
    ]
    draw.polygon(inner_shield, fill=(33, 150, 243, 255))
    
    # Eye symbol in center (white)
    # Eye outline
    draw.ellipse([11, 13, 21, 19], fill=(255, 255, 255, 255))
    # Pupil
    draw.ellipse([14, 14, 18, 18], fill=(25, 118, 210, 255))
    
    # Save the icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.png")
    img.save(icon_path, "PNG")
    print(f"✅ Icon created: {icon_path}")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("❌ PIL (Pillow) not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "pillow"])
        create_icon()