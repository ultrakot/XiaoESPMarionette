from machine import Pin
import time

# Configure the LED pin
# Most ESP32-C6 development boards have a built-in LED
# Check your board's pinout to confirm the correct pin number
led = Pin(8, Pin.OUT)  # Change pin number if needed for your board

def blink_led():
    while True:
        try:
            # Turn LED on
            led.on()
            time.sleep(0.5)  # Wait for 500ms
            
            # Turn LED off
            led.off()
            time.sleep(0.5)  # Wait for 500ms
            
        except KeyboardInterrupt:
            # Clean up on ctrl-c
            led.off()
            break

# Run the blink function
if __name__ == "__main__":
    print("Starting LED blink. Press Ctrl+C to stop.")
    blink_led()
