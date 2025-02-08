# main.py

import time
import json
import machine
from machine import Pin
from tmc2130 import TMC_2130, MovementAbsRel  # Adjust the import as needed

# --------------------------
# Button configuration
# --------------------------
# Assumes buttons are wired active-low (pressed = 0)
BUTTON_CW_PIN         = 10  # move clockwise (one-step while pressed)
BUTTON_CCW_PIN        = 11  # move counter-clockwise (one-step while pressed)
BUTTON_PRESET1_PIN    = 12  # preset 1 button (short press: move to preset1; long press: save preset1)
BUTTON_PRESET2_PIN    = 13  # preset 2 button (short press: move to preset2; long press: save preset2)

button_cw      = Pin(BUTTON_CW_PIN, Pin.IN, Pin.PULL_UP)
button_ccw     = Pin(BUTTON_CCW_PIN, Pin.IN, Pin.PULL_UP)
button_preset1 = Pin(BUTTON_PRESET1_PIN, Pin.IN, Pin.PULL_UP)
button_preset2 = Pin(BUTTON_PRESET2_PIN, Pin.IN, Pin.PULL_UP)

# --------------------------
# Motor Driver configuration
# --------------------------
STEP_PIN = 14
DIR_PIN  = 15
EN_PIN   = 16
SPI_ID   = 1
CS_PIN   = 17
SPI_BAUDRATE = 1000000

# Instantiate the TMC2130 driver (SPI based)
driver = TMC_2130(pin_step=STEP_PIN,
                  pin_dir=DIR_PIN,
                  pin_en=EN_PIN,
                  spi_id=SPI_ID,
                  cs_pin=CS_PIN,
                  baudrate=SPI_BAUDRATE)

# Set loglevel (optional)
driver.setLoglevel(driver.Loglevel.info)

# --------------------------
# JSON File Handling
# --------------------------
POSITIONS_FILE = "positions.json"

def load_positions():
    """Load preset positions from a JSON file. Returns a dict with keys 'preset1' and 'preset2'."""
    try:
        with open(POSITIONS_FILE, "r") as f:
            positions = json.load(f)
        print("Loaded positions:", positions)
    except Exception as e:
        print("Could not load positions file. Using defaults. Error:", e)
        positions = {"preset1": 0, "preset2": 0}
    return positions

def save_positions(positions):
    """Save the preset positions to the JSON file."""
    try:
        with open(POSITIONS_FILE, "w") as f:
            json.dump(positions, f)
        print("Positions saved:", positions)
    except Exception as e:
        print("Error saving positions:", e)

# Load stored positions at startup.
positions = load_positions()

# --------------------------
# Debounce and long-press thresholds (in seconds)
# --------------------------
DEBOUNCE_TIME = 0.05        # 50 ms debounce
LONG_PRESS_THRESHOLD = 2    # 2 seconds for long press

# --------------------------
# Helper functions
# --------------------------
def wait_for_release(button):
    """Wait until the given button is released (goes high)."""
    while button.value() == 0:
        time.sleep(0.05)

def long_press_detect(button):
    """Return True if the button remains pressed for LONG_PRESS_THRESHOLD seconds."""
    start = time.ticks_ms()
    while button.value() == 0:
        if time.ticks_diff(time.ticks_ms(), start) > LONG_PRESS_THRESHOLD * 1000:
            return True
        time.sleep(0.05)
    return False

# --------------------------
# Main loop
# --------------------------
print("Starting main loop. Use the buttons to control the motor.")

while True:
    # --- Button 1: Move clockwise one step while pressed ---
    if button_cw.value() == 0:
        print("Button CW pressed: stepping clockwise.")
        current_pos = driver.getCurrentPosition()
        driver.runToPositionSteps(current_pos + 1, movement_abs_rel=MovementAbsRel.absolute)
        time.sleep(DEBOUNCE_TIME)

    # --- Button 2: Move counter-clockwise one step while pressed ---
    if button_ccw.value() == 0:
        print("Button CCW pressed: stepping counter-clockwise.")
        current_pos = driver.getCurrentPosition()
        driver.runToPositionSteps(current_pos - 1, movement_abs_rel=MovementAbsRel.absolute)
        time.sleep(DEBOUNCE_TIME)

    # --- Button 3: Preset 1 ---
    if button_preset1.value() == 0:
        print("Button PRESET1 pressed.")
        # Determine if this is a long press or a short press.
        if long_press_detect(button_preset1):
            # Long press: update preset1 with the current position and save to JSON.
            positions["preset1"] = driver.getCurrentPosition()
            print("Preset 1 updated to:", positions["preset1"])
            save_positions(positions)
            wait_for_release(button_preset1)
        else:
            # Short press: command move to preset1.
            print("Moving to preset 1:", positions["preset1"])
            driver.runToPositionSteps(positions["preset1"], movement_abs_rel=MovementAbsRel.absolute)
            wait_for_release(button_preset1)

    # --- Button 4: Preset 2 ---
    if button_preset2.value() == 0:
        print("Button PRESET2 pressed.")
        # Determine if this is a long press or a short press.
        if long_press_detect(button_preset2):
            # Long press: update preset2 with the current position and save to JSON.
            positions["preset2"] = driver.getCurrentPosition()
            print("Preset 2 updated to:", positions["preset2"])
            save_positions(positions)
            wait_for_release(button_preset2)
        else:
            # Short press: command move to preset2.
            print("Moving to preset 2:", positions["preset2"])
            driver.runToPositionSteps(positions["preset2"], movement_abs_rel=MovementAbsRel.absolute)
            wait_for_release(button_preset2)

    # Small delay to reduce CPU load
    time.sleep(0.01)
