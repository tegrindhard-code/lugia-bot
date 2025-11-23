# PyAutoGUI Coordinate Calibration Guide

This guide will help you find the correct coordinates for automating Roblox Studio.

## Quick Start

### Step 1: Install Additional Dependencies (Optional)

For the Window Finder feature (Windows only):
```bash
pip install pygetwindow
```

### Step 2: Run the Coordinate Finder

```bash
python find_coordinates.py
```

## Finding Coordinates

### Method 1: Position Tracker (Recommended for Beginners)

1. Run `find_coordinates.py` and select option **1** (Position Tracker)
2. Open Roblox Studio and position it on your screen
3. Move your mouse over each UI element you need
4. Write down the X and Y coordinates displayed
5. Press Ctrl+C when done

**UI Elements to Find:**
- **File Menu**: Top-left, "File" text in menu bar
- **New Button**: In File dropdown menu
- **Baseplate Template**: Template selection window
- **Create Button**: Bottom of template window
- **Publish Menu**: "Publish to Roblox" in File menu
- **Game Name Field**: Input field for game name
- **Publish Button**: Final button to publish

### Method 2: Click Recorder (Recommended for Advanced Users)

1. Run `find_coordinates.py` and select option **3** (Click Recorder)
2. When recording starts, open Roblox Studio
3. Click through the entire process:
   - Click File
   - Click New
   - Click Baseplate
   - Click Create
   - (Wait for load)
   - Click File
   - Click Publish to Roblox
   - Click in name field
   - (Type would happen here)
   - Click Publish button

4. The script will automatically save all coordinates to a JSON file
5. Review the generated Python code in the console

### Method 3: Screenshot Mode

1. Run `find_coordinates.py` and select option **2** (Screenshot Mode)
2. Position Roblox Studio on your screen
3. Script will take a screenshot after 3 seconds
4. Open the screenshot and manually find coordinates

## Updating Configuration

After finding coordinates, update `studio_coordinates.json`:

```json
{
  "screen_resolution": {
    "width": 1920,
    "height": 1080
  },
  "roblox_studio": {
    "file_menu": {
      "x": 50,
      "y": 30,
      "comment": "File menu in top menu bar"
    },
    "new_button": {
      "x": 100,
      "y": 100,
      "comment": "New option in File menu"
    },
    "baseplate_template": {
      "x": 300,
      "y": 300,
      "comment": "Baseplate template icon"
    },
    "create_button": {
      "x": 500,
      "y": 500,
      "comment": "Create button in template window"
    },
    "publish_menu": {
      "x": 150,
      "y": 150,
      "comment": "Publish to Roblox in File menu"
    },
    "game_name_field": {
      "x": 400,
      "y": 300,
      "comment": "Game name input field"
    },
    "publish_button": {
      "x": 600,
      "y": 500,
      "comment": "Final publish button"
    }
  }
}
```

## Testing Your Coordinates

### Simple Test Script

Create a test file `test_coordinates.py`:

```python
import pyautogui
import time
import json

# Load coordinates
with open('studio_coordinates.json', 'r') as f:
    coords = json.load(f)

# Test each coordinate
studio = coords['roblox_studio']

print("This will move your mouse to each coordinate.")
print("Make sure Roblox Studio is open and visible!")
print("Starting in 3 seconds...\n")
time.sleep(3)

for name, coord in studio.items():
    if isinstance(coord, dict) and 'x' in coord:
        print(f"Moving to {name}: ({coord['x']}, {coord['y']})")
        pyautogui.moveTo(coord['x'], coord['y'], duration=1)
        time.sleep(2)

print("\nDone! Did the mouse move to the correct locations?")
```

Run it:
```bash
python test_coordinates.py
```

## Important Tips

### Screen Resolution
- Coordinates are **screen-specific**
- If you change resolution, recalibrate coordinates
- Use the same monitor/display settings always

### Roblox Studio Position
- Keep Studio in the same position on screen
- Consider maximizing Studio for consistency
- Coordinates change if you resize or move the window

### Safety Features

PyAutoGUI has a failsafe:
- **Move mouse to top-left corner** of screen to stop automation
- This stops all PyAutoGUI operations immediately

### Common Issues

**Mouse moves to wrong location:**
- Verify screen resolution matches your actual resolution
- Check if Studio is maximized or windowed
- Recalibrate coordinates

**Elements not clickable:**
- Add delays (`time.sleep()`) between actions
- Ensure Studio is the active window
- Check if menus are actually open before clicking

**Coordinates seem random:**
- Check if you have multiple monitors
- Verify coordinate system (0,0 is top-left of primary monitor)
- Make sure Studio is on primary monitor

## Example: Complete Calibration Workflow

1. **Start the finder:**
   ```bash
   python find_coordinates.py
   ```

2. **Choose Click Recorder (option 3)**

3. **Open Roblox Studio and position it**

4. **When recording starts, click through:**
   - File → New → Baseplate → Create
   - File → Publish to Roblox → Name Field → Publish

5. **Review the saved JSON file**
   - File will be named like `coordinates_20240101_120000.json`

6. **Copy coordinates to `studio_coordinates.json`**

7. **Test with the test script above**

8. **Try `/automate_publish` command in Discord**

## Advanced: Automatic Coordinate Detection

For advanced users, you can try to detect UI elements programmatically using image recognition:

```python
import pyautogui

# Take a screenshot of the element you want to find
# Then use locateOnScreen
location = pyautogui.locateOnScreen('file_button.png')

if location:
    # Get center of the found element
    x, y = pyautogui.center(location)
    print(f"Found at: {x}, {y}")
```

## Troubleshooting

### Coordinate Finder Won't Start
```bash
pip install pyautogui pillow
```

### Window Finder Doesn't Work
```bash
pip install pygetwindow  # Windows only
```

### Permission Errors
- On Mac: Grant Terminal accessibility permissions
- System Preferences → Security & Privacy → Accessibility

### Coordinates Keep Changing
- Use **windowed mode** with fixed size instead of fullscreen
- Set Roblox Studio to always open in same position
- Consider scripting the window position before automation

## Best Practices

1. **Always test coordinates** before using in production
2. **Keep a backup** of working coordinates
3. **Document your screen resolution** in the JSON file
4. **Use descriptive comments** for each coordinate
5. **Add delays** between clicks for reliability
6. **Handle errors gracefully** in automation scripts

## Need Help?

If you're still having issues:
1. Check that PyAutoGUI is installed correctly
2. Verify Roblox Studio is on your primary monitor
3. Try the Position Tracker method manually
4. Use screenshot mode to visually verify locations
5. Test coordinates with the simple test script above

---

**Remember:** PyAutoGUI automation requires your computer to be unlocked and active. It physically moves your mouse and types - you cannot use your computer during automation!
