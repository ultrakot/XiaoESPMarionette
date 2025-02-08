from machine import Pin, SPI, Timer
import struct
import time
import ujson
from cube_stepper_driver import Stepper as CubeDriver
from frence_stepper_driver import Stepper as FrenchDriver

# ================================
# TMC2130 SPI driver configuration
# ================================

# Define pins for SPI-based communication with the TMC2130
# (Adjust these pin numbers as needed for your hardware)
cs_pin = Pin(4, Pin.OUT)       # Chip select for SPI
cs_pin.value(1)                # CS high initially

spi = SPI(-1,
          baudrate=100000,
          polarity=1,
          phase=1,
          firstbit=SPI.MSB,
          sck=Pin(19, Pin.OUT),
          mosi=Pin(18, Pin.OUT),
          miso=Pin(20, Pin.IN))

# TMC2130 register addresses and flags
WRITE_FLAG = 0x80
READ_FLAG = 0x00
REG_GCONF      = 0x00
REG_IHOLD_IRUN = 0x10
REG_CHOPCONF   = 0x6C
REG_COOLCONF   = 0x6D
REG_DRVSTATUS  = 0x6F

def pack_data(data, fmt='>L'):
    """Pack data into a bytearray for SPI communication."""
    return bytearray(struct.pack(fmt, data))

def tmc_write(reg, data):
    """Write 32-bit data to a TMC2130 register."""
    cs_pin.value(0)  # Select chip
    spi.write(pack_data(reg, 'B'))  # Write register address (1 byte)
    spi.write(pack_data(data))      # Write 4 bytes of data
    cs_pin.value(1)  # Deselect chip

def tmc_read(reg):
    """Read 32-bit data from a TMC2130 register."""
    cs_pin.value(0)
    # Send a dummy write to request reading from register reg:
    tmc_write(reg, 0x00)
    # Then send register address again and read 4 bytes:
    spi.write(pack_data(reg, 'B'))
    data = spi.read(4, 0x00)
    cs_pin.value(1)
    return struct.unpack('>L', data)[0]

def setup_driver():
    """Initialize the TMC2130 driver with basic settings."""
    spi.init(baudrate=100000)
    # Enable voltage mode (AIN as reference)
    tmc_write(WRITE_FLAG + REG_GCONF, 0x00000001)
    # Set current (IHOLD=0x10, IRUN=0x10)
    tmc_write(WRITE_FLAG + REG_IHOLD_IRUN, 0x00001010)
    # Configure chopper (256 microsteps, basic settings)
    tmc_write(WRITE_FLAG + REG_CHOPCONF, 0x20008008)

def test_spi_connection():
    """Test SPI connection by writing/reading a test pattern."""
    print("Testing SPI connection...")
    test_value = 0x12345678
    print("Writing test pattern to COOLCONF: 0x{:08X}".format(test_value))
    tmc_write(WRITE_FLAG + REG_COOLCONF, test_value)
    readback = tmc_read(REG_COOLCONF)
    print("Read back from COOLCONF: 0x{:08X}".format(readback))
    if readback == test_value:
        print("COOLCONF write/read test: PASSED")
        return True
    else:
        print("COOLCONF write/read test: FAILED")
        return False

# ================================
# Stepper Motor (simulation) Class
# ================================
class StepperMotor:
    def __init__(self):
        # This example uses a simulated current_position.
        self.current_position = 0

    def move_to(self, target_position):
        """Simulate moving the motor from current_position to target_position.
           After each step, check for a stall condition via stallguard.
        """
        if target_position == self.current_position:
            print("Already at position", self.current_position)
            return

        step_delay = 0.01  # delay between simulated steps (in seconds)
        print("Moving from {} to {}".format(self.current_position, target_position))
        if target_position > self.current_position:
            step = 1
        else:
            step = -1

        # Move one simulated step at a time.
        while self.current_position != target_position:
            self.current_position += step
            print("Step: position =", self.current_position)
            time.sleep(step_delay)
            check_stallguard()  # check DRVSTATUS for stallguard condition
        print("Reached position", self.current_position)

    def move_up(self, steps=100):
        self.move_to(self.current_position + steps)

    def move_down(self, steps=100):
        self.move_to(self.current_position - steps)

# ================================
# Position persistence for Button 4 (using JSON)
# ================================
def load_position():
    """Load position B from 'position.json'. If not available, return 0."""
    try:
        with open("position.json", "r") as f:
            data = ujson.load(f)
            pos = data.get("posB", 0)
            print("Loaded posB =", pos)
            return pos
    except Exception as e:
        print("Error loading position.json:", e)
        return 0

def save_position(pos):
    """Save position B into 'position.json'."""
    try:
        with open("position.json", "w") as f:
            ujson.dump({"posB": pos}, f)
        print("Saved posB =", pos)
    except Exception as e:
        print("Error saving position.json:", e)

# ================================
# StallGuard Checker
# ================================
def check_stallguard():
    """Read DRVSTATUS and print 'stallguard!' if condition met.
       (For example, we assume a stall if the 8-bit StallGuard value is below 5.)
    """
    status = tmc_read(REG_DRVSTATUS)
    stallguard_val = (status >> 24) & 0xFF
    if stallguard_val < 5:
        print("stallguard!")

# ================================
# Button handling (with short vs long press)
# ================================
# Global dictionary to store press start times for each button
press_times = {}
# Global variable for position A (set by button 3)
posA = None
# Define a threshold (in ms) to distinguish long press from short press.
LONG_PRESS_THRESHOLD = 1000  # 1000 ms = 1 second

def button_irq_handler(pin):
    """Generic IRQ handler for buttons.
       It uses the pin's name (assigned in the pin object) to decide which action to take.
       Assumes buttons are wired with an internal pull-up so that:
         - pressed = 0 (LOW)
         - released = 1 (HIGH)
    """
    global posA
    button_name = pin.name  # we will assign a unique name to each button
    current_val = pin.value()
    now = time.ticks_ms()

    if current_val == 0:  # button pressed: record timestamp
        press_times[button_name] = now
    else:  # button released: determine press duration
        press_duration = time.ticks_diff(now, press_times.get(button_name, now))
        # --- Process based on button name ---
        if button_name == "btn_up":
            # For button 1, any release is a short press: go up.
            print("[Button UP] Short press detected ({} ms)".format(press_duration))
            stepper_motor.move_up(steps=100)
        elif button_name == "btn_down":
            print("[Button DOWN] Short press detected ({} ms)".format(press_duration))
            stepper_motor.move_down(steps=100)
        elif button_name == "btn_posA":
            if press_duration >= LONG_PRESS_THRESHOLD:
                # Long press: set position A to the current motor position.
                posA = stepper_motor.current_position
                print("[Button posA] Long press: Set posA =", posA)
            else:
                # Short press: move to position A (if set).
                if posA is not None:
                    print("[Button posA] Short press: Moving to posA =", posA)
                    stepper_motor.move_to(posA)
                else:
                    print("[Button posA] Short press: posA not set yet.")
        elif button_name == "btn_posB":
            if press_duration >= LONG_PRESS_THRESHOLD:
                # Long press: set position B to current position and save to file.
                posB = stepper_motor.current_position
                print("[Button posB] Long press: Set posB =", posB)
                save_position(posB)
            else:
                # Short press: read position B from file and move there.
                posB = load_position()
                print("[Button posB] Short press: Moving to posB =", posB)
                stepper_motor.move_to(posB)

# ================================
# Main code
# ================================

# Create a single instance of the StepperMotor
stepper_motor = StepperMotor()

def main():
    global stepper_motor

    # Setup driver over SPI
    setup_driver()
    if not test_spi_connection():
        print("SPI communication test failed. Exiting.")
        return

    # -------------------------------
    # Setup buttons with IRQ callbacks.
    # (Assign unique names to each button using an attribute.)
    # -------------------------------
    # Adjust the pin numbers for your hardware.
    btn_up = Pin(12, Pin.IN, Pin.PULL_UP)
    btn_up.name = "btn_up"
    btn_up.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_irq_handler)

    btn_down = Pin(13, Pin.IN, Pin.PULL_UP)
    btn_down.name = "btn_down"
    btn_down.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_irq_handler)

    btn_posA = Pin(14, Pin.IN, Pin.PULL_UP)
    btn_posA.name = "btn_posA"
    btn_posA.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_irq_handler)

    # Use a different pin for position B button (avoid conflict with other functions)
    btn_posB = Pin(27, Pin.IN, Pin.PULL_UP)
    btn_posB.name = "btn_posB"
    btn_posB.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_irq_handler)

    # -------------------------------
    # Setup a periodic timer to poll the stallguard status.
    # -------------------------------
    stallguard_timer = Timer(-1)
    stallguard_timer.init(period=500, mode=Timer.PERIODIC,
                          callback=lambda t: check_stallguard())

    # Main loop – your program can do other tasks here.
    while True:
        # For example, print the current motor position every second.
        print("Current motor position:", stepper_motor.current_position)
        time.sleep(1)

if __name__ == "__main__":
    main()
