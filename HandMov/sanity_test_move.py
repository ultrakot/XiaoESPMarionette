from machine import Pin
import time

# Initialize pins
dir_pin = Pin(0, Pin.OUT)
step_pin = Pin(1, Pin.OUT)
enable_pin = Pin(2, Pin.OUT)


enable_pin.value(0)  # Set to 0 to ENABLE the driver
time.sleep(1)


# Main loop
while True:
    step_pin.value(1)
    time.sleep_us(2)
    step_pin.value(0)
    time.sleep_us(2)

