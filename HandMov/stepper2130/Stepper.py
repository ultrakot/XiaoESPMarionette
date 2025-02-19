from machine import Pin
import time

class Stepper:
    def __init__(self, dir_pin=0, step_pin=1, enable_pin=2):
        # Initialize pins
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.enable_pin = Pin(enable_pin, Pin.OUT)
        
        self.current_position = 0
        self.is_moving = False
        
        # Enable driver (active LOW for TMC2130)
        self.enable_pin.value(0)
    
    def enable(self):
        """Enable the motor driver"""
        self.enable_pin.value(0)
        
    def disable(self):
        """Disable the motor driver"""
        self.enable_pin.value(1)
    
    def single_step(self, direction):
        """Make a single step in specified direction"""
        self.dir_pin.value(direction)
        self.step_pin.value(1)
        time.sleep_us(5)  # Ensure step pulse width
        self.step_pin.value(0)
        time.sleep_us(5)
        self.current_position += (1 if direction else -1)
    
    def move_steps(self, steps, direction):
        """Move a specific number of steps"""
        self.is_moving = True
        for _ in range(abs(steps)):
            self.single_step(direction)
            time.sleep_ms(1)
        self.is_moving = False
