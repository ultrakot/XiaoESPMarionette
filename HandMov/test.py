from machine import Pin
import time

class BasicStepper:
    def __init__(self, dir_pin, step_pin,en_pin):
        """
        Initialize basic stepper control
        dir_pin: Direction pin number
        step_pin: Step pin number
        """
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.en_pin = Pin(en_pin, Pin.OUT)
        self.en_pin.value(1) 
        
    def move(self, steps, direction=1):
        """
        Move stepper motor
        steps: Number of steps to move
        direction: 1 for forward, 0 for backward
        """
        self.en_pin.value(0)
        time.sleep_ms(1) 
        # Set direction
        self.dir_pin.value(direction)
        
        # Make steps
        for _ in range(steps):
            self.step_pin.value(1)  # Step high
            time.sleep_ms(2)        # Wait 2ms
            self.step_pin.value(0)  # Step low
            time.sleep_ms(2)        # Wait 2ms

# Example usage
if __name__ == '__main__':
    # Create stepper instance (adjust pins as needed)
    stepper = BasicStepper(dir_pin=0, step_pin=1, en_pin=2)
    
    # Move 200 steps forward
    stepper.move(2000, direction=1)
    
    time.sleep(1)  # Wait 1 second
    
    # Move 200 steps backward
    stepper.move(200, direction=0)