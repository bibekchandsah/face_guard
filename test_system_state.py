#!/usr/bin/env python3
"""
Test script for system state detection improvements
"""
import ctypes
import ctypes.wintypes
from ctypes import wintypes
import time

def is_system_locked():
    """Check if Windows screen is locked using multiple methods"""
    try:
        # Method 1: Check if we can open the input desktop
        hdesk = ctypes.windll.user32.OpenInputDesktop(0, False, 0)
        if hdesk == 0:
            return True  # Can't access desktop, likely locked
        
        # Method 2: Get desktop name and check if it's the secure desktop
        desktop_name = ctypes.create_unicode_buffer(256)
        result = ctypes.windll.user32.GetUserObjectInformationW(hdesk, 2, desktop_name, 512, None)
        ctypes.windll.user32.CloseDesktop(hdesk)
        
        if result:
            desktop_str = desktop_name.value.lower()
            print(f"Desktop name: '{desktop_str}'")
            # Check for secure desktop names that indicate lock screen
            if desktop_str in ["winlogon", "secure desktop", ""] or "winlogon" in desktop_str:
                return True
        
        # Method 3: Check if screen saver is active (additional check)
        screen_saver_running = ctypes.c_bool()
        ctypes.windll.user32.SystemParametersInfoW(0x0072, 0, ctypes.byref(screen_saver_running), 0)
        if screen_saver_running.value:
            return True
            
        return False
    except Exception as e:
        print(f"Error checking lock state: {e}")
        # If we can't determine the state, assume not locked to avoid false positives
        return False

def is_system_sleeping():
    """Check if system is in sleep/hibernate mode or display is off"""
    try:
        # Method 1: Check system power state
        class SYSTEM_POWER_STATUS(ctypes.Structure):
            _fields_ = [
                ("ACLineStatus", ctypes.c_ubyte),
                ("BatteryFlag", ctypes.c_ubyte),
                ("BatteryLifePercent", ctypes.c_ubyte),
                ("SystemStatusFlag", ctypes.c_ubyte),
                ("BatteryLifeTime", wintypes.DWORD),
                ("BatteryFullLifeTime", wintypes.DWORD)
            ]
        
        power_status = SYSTEM_POWER_STATUS()
        result = ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(power_status))
        if result:
            print(f"Power status - AC: {power_status.ACLineStatus}, Battery: {power_status.BatteryLifePercent}%, System Status: {power_status.SystemStatusFlag}")
            # SystemStatusFlag bit 0 indicates if system is in power saving mode
            if power_status.SystemStatusFlag & 1:
                return True
        
        return False
    except Exception as e:
        print(f"Error checking sleep state: {e}")
        return False

def main():
    """Test system state detection"""
    print("Testing system state detection...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            locked = is_system_locked()
            sleeping = is_system_sleeping()
            
            status = []
            if locked:
                status.append("LOCKED")
            if sleeping:
                status.append("SLEEPING")
            if not locked and not sleeping:
                status.append("ACTIVE")
            
            print(f"System state: {' | '.join(status)}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest completed.")

if __name__ == "__main__":
    main()