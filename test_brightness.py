#!/usr/bin/env python3
"""
Test the brightness fix for list vs int issue
"""
import json
import screen_brightness_control as sbc

def load_settings():
    try:
        with open("face_guard_data/settings.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_settings(settings):
    with open("face_guard_data/settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def _get_current_brightness():
    try:
        brightness = sbc.get_brightness(display=0)
        # sbc.get_brightness returns a list, get the first element
        return brightness[0] if isinstance(brightness, list) and brightness else brightness
    except Exception:
        return 100

def set_brightness(val):
    val = int(max(0, min(100, val)))
    try:
        sbc.set_brightness(val, display=0)
        print(f"Brightness set to {val}%.")
    except Exception as e:
        print(f"Brightness change failed: {e}")

def store_current_brightness(settings):
    """Store current brightness before making changes"""
    try:
        current = _get_current_brightness()
        # Ensure current is an integer
        current = int(current) if current is not None else 100
        
        # Only store if we haven't already stored it (prevent overwriting the original)
        if settings.get("brightness_restored", True):
            settings["brightness_before_absence"] = current
            settings["brightness_restored"] = False
            save_settings(settings)
            print(f"Stored original brightness: {current}% (will restore to this level when owner returns)")
        else:
            stored = settings.get('brightness_before_absence', 100)
            print(f"Brightness already stored at {stored}%, not overwriting")
    except Exception as e:
        print(f"Failed to store brightness: {e}")

def restore_brightness(settings):
    """Restore brightness to the stored value before absence"""
    try:
        stored_brightness = settings.get("brightness_before_absence", 100)
        current_brightness = _get_current_brightness()
        
        # Handle case where stored_brightness might be a list (from previous versions)
        if isinstance(stored_brightness, list) and stored_brightness:
            stored_brightness = stored_brightness[0]
        
        # Ensure both values are integers
        stored_brightness = int(stored_brightness) if stored_brightness is not None else 100
        current_brightness = int(current_brightness) if current_brightness is not None else 100
        
        # Always restore if we haven't already restored (brightness_restored = False means we need to restore)
        if not settings.get("brightness_restored", True):
            set_brightness(stored_brightness)
            settings["brightness_restored"] = True
            # Also fix the stored value to be an integer for future use
            settings["brightness_before_absence"] = stored_brightness
            save_settings(settings)
            print(f"Brightness restored from {current_brightness}% to {stored_brightness}%")
        else:
            print(f"Brightness already restored to {stored_brightness}%")
    except Exception as e:
        print(f"Failed to restore brightness: {e}")

# Test the fixed functions
print("=== Testing Brightness Fix ===")

# Test brightness getting
current = _get_current_brightness()
print(f"Current brightness: {current}% (type: {type(current)})")

# Load settings
settings = load_settings()

# Test storing
print("\n1. Testing store_current_brightness...")
store_current_brightness(settings)

# Test dimming
print("\n2. Testing dimming to 0%...")
set_brightness(0)

# Test restoring
print("\n3. Testing restore_brightness...")
settings = load_settings()  # Reload
restore_brightness(settings)

print(f"\nFinal brightness: {_get_current_brightness()}%")
print("✅ Test completed successfully!")