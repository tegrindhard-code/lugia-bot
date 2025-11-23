"""
PyAutoGUI Coordinate Finder for Roblox Studio Automation

This script helps you find the exact coordinates needed for automating
Roblox Studio with PyAutoGUI.

Usage:
1. Run this script: python find_coordinates.py
2. Choose a mode:
   - Position Tracker: Move your mouse to find coordinates
   - Screenshot Mode: Take a screenshot with coordinate grid
   - Click Recorder: Record clicks and save coordinates
"""

import pyautogui
import time
import sys
import json
from datetime import datetime

# Disable PyAutoGUI's failsafe (move mouse to corner to stop)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


class CoordinateFinder:
    def __init__(self):
        self.recorded_clicks = []
        self.screen_width, self.screen_height = pyautogui.size()

    def display_info(self):
        """Display screen information"""
        print("\n" + "="*60)
        print("PyAutoGUI Coordinate Finder")
        print("="*60)
        print(f"Screen Resolution: {self.screen_width} x {self.screen_height}")
        print(f"Current Mouse Position: {pyautogui.position()}")
        print("="*60 + "\n")

    def position_tracker(self):
        """Track mouse position in real-time"""
        print("\n📍 POSITION TRACKER MODE")
        print("-" * 60)
        print("Move your mouse to find coordinates")
        print("Press Ctrl+C to stop")
        print("-" * 60 + "\n")

        try:
            while True:
                x, y = pyautogui.position()
                position_str = f"X: {x:4d}  Y: {y:4d}"

                # Print on same line
                print(f"\r{position_str}", end='', flush=True)
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n✓ Position tracker stopped\n")

    def screenshot_with_grid(self):
        """Take a screenshot with coordinate grid overlay"""
        print("\n📸 SCREENSHOT MODE")
        print("-" * 60)
        print("Taking screenshot in 3 seconds...")
        print("Position your Roblox Studio window now!")
        print("-" * 60)

        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        # Take screenshot
        screenshot = pyautogui.screenshot()
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(filename)

        print(f"\n✓ Screenshot saved as: {filename}")
        print(f"  Size: {screenshot.size}")
        print("\nNow you can open this image and find coordinates manually\n")

    def click_recorder(self):
        """Record mouse clicks and save coordinates"""
        print("\n🖱️  CLICK RECORDER MODE")
        print("-" * 60)
        print("This will record your clicks for 30 seconds")
        print("Click on the UI elements you want to automate in Roblox Studio")
        print("\nStarting in 3 seconds...")
        print("-" * 60)

        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        print("\n✓ Recording started! Make your clicks now...")
        print("(Recording will stop automatically after 30 seconds or press Ctrl+C)\n")

        start_time = time.time()
        last_click = None

        try:
            while time.time() - start_time < 30:
                if pyautogui.mouseDown():
                    current_pos = pyautogui.position()

                    # Avoid duplicate clicks
                    if current_pos != last_click:
                        click_data = {
                            "position": current_pos,
                            "timestamp": time.time() - start_time,
                            "x": current_pos[0],
                            "y": current_pos[1]
                        }
                        self.recorded_clicks.append(click_data)
                        print(f"  Click #{len(self.recorded_clicks)}: X={current_pos[0]}, Y={current_pos[1]}")
                        last_click = current_pos

                    time.sleep(0.2)

        except KeyboardInterrupt:
            print("\n✓ Recording stopped by user\n")

        if self.recorded_clicks:
            self.save_coordinates()
        else:
            print("No clicks recorded!\n")

    def save_coordinates(self):
        """Save recorded coordinates to file"""
        filename = f"coordinates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "screen_resolution": {
                "width": self.screen_width,
                "height": self.screen_height
            },
            "clicks": self.recorded_clicks
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Coordinates saved to: {filename}")
        print(f"  Total clicks recorded: {len(self.recorded_clicks)}\n")

        # Display Python code
        print("Python Code:")
        print("-" * 60)
        for i, click in enumerate(self.recorded_clicks, 1):
            print(f"# Click {i} (at {click['timestamp']:.1f}s)")
            print(f"pyautogui.click({click['x']}, {click['y']})")
            print(f"time.sleep(1)  # Wait 1 second")
            print()

    def find_roblox_studio_window(self):
        """Try to find Roblox Studio window (Windows only)"""
        print("\n🔍 WINDOW FINDER MODE")
        print("-" * 60)

        try:
            import pygetwindow as gw

            windows = gw.getAllTitles()
            roblox_windows = [w for w in windows if 'Roblox Studio' in w or 'Studio' in w]

            if roblox_windows:
                print("Found Roblox Studio windows:")
                for i, window in enumerate(roblox_windows, 1):
                    win = gw.getWindowsWithTitle(window)[0]
                    print(f"\n  {i}. {window}")
                    print(f"     Position: ({win.left}, {win.top})")
                    print(f"     Size: {win.width} x {win.height}")
            else:
                print("No Roblox Studio windows found!")
                print("Make sure Roblox Studio is open.")

        except ImportError:
            print("⚠️  pygetwindow not installed")
            print("Install with: pip install pygetwindow")
            print("\nThis feature is Windows-only.")

        print()

    def calibration_guide(self):
        """Display calibration guide for Roblox Studio"""
        print("\n📋 ROBLOX STUDIO CALIBRATION GUIDE")
        print("="*60)
        print("""
For Roblox Studio automation, you need to find coordinates for:

1. File Menu
   - Location: Top-left corner of Studio
   - Find: Click "File" in menu bar

2. New Button
   - Location: File menu dropdown
   - Find: "New" option in File menu

3. Baseplate Template
   - Location: Template selection window
   - Find: "Baseplate" template icon

4. Create Button
   - Location: Template window bottom
   - Find: Blue "Create" button

5. Publish to Roblox
   - Location: File > Publish to Roblox
   - Find: Menu item or toolbar button

Steps to calibrate:
1. Run this script in Position Tracker mode
2. Open Roblox Studio
3. Hover over each UI element
4. Note down the coordinates
5. Update featureUPLOADANDSTATUS.py with the coordinates

Alternative: Use Click Recorder mode
1. Run Click Recorder
2. Open Roblox Studio
3. Click through the entire publishing process
4. The script will save all coordinates automatically
        """)
        print("="*60 + "\n")


def main():
    finder = CoordinateFinder()

    while True:
        finder.display_info()

        print("Select a mode:")
        print("  1. Position Tracker (real-time coordinate display)")
        print("  2. Screenshot Mode (take screenshot for manual inspection)")
        print("  3. Click Recorder (record clicks automatically)")
        print("  4. Window Finder (find Roblox Studio window)")
        print("  5. Calibration Guide (view guide)")
        print("  6. Exit")
        print()

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            finder.position_tracker()
        elif choice == '2':
            finder.screenshot_with_grid()
        elif choice == '3':
            finder.click_recorder()
        elif choice == '4':
            finder.find_roblox_studio_window()
        elif choice == '5':
            finder.calibration_guide()
        elif choice == '6':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please try again.\n")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...\n")
        sys.exit(0)
