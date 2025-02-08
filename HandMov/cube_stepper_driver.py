from machine import Pin
import time

class Stepper:
    def __init__(self, dir_pin, step_pin, ms_pin=None):
        """
        Initialize the stepper motor with given direction, step, and optional microstepping pins.
        """
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.ms_pin = ms_pin  # This pin can be used to control microstepping if needed

        # Ensure the pins are in a known state
        self.dir_pin.value(0)
        self.step_pin.value(0)
        if self.ms_pin is not None:
            self.ms_pin.value(0)

        self.position = 0  # Current position in steps

    def move_to(self, target_position, initial_delay, min_delay, overshoot=0):
        """
        Move the stepper motor to a target position using a linear acceleration/deceleration ramp.
        
        Parameters:
            target_position (int): The desired position in steps.
            initial_delay (int): Delay in microseconds at the start/finish (slower speed).
            min_delay (int): Minimum delay in microseconds between steps (maximum speed).
            overshoot (int): Extra steps to overshoot before reversing for a precise stop.
        """
        steps_needed = abs(target_position - self.position)
        if steps_needed == 0:
            return  # No movement needed

        # Set direction: using 1 for forward and 0 for reverse.
        if target_position > self.position:
            self.dir_pin.value(1)
            move_direction = 1
        else:
            self.dir_pin.value(0)
            move_direction = -1

        # Total steps include any overshoot
        total_steps = steps_needed + overshoot
        ramp_steps = total_steps // 2
        # Calculate the decrement per step for a linear ramp
        delay_decrement = (initial_delay - min_delay) / ramp_steps if ramp_steps > 0 else 0

        # Execute the movement with acceleration and deceleration
        for step_index in range(total_steps):
            if step_index < ramp_steps:
                # Acceleration phase: decrease delay to speed up
                current_delay = initial_delay - delay_decrement * (step_index + 1)
                current_delay = max(current_delay, min_delay)
            elif step_index >= total_steps - ramp_steps:
                # Deceleration phase: increase delay to slow down
                decel_index = step_index - (total_steps - ramp_steps)
                current_delay = min_delay + delay_decrement * (decel_index + 1)
            else:
                # Constant speed phase
                current_delay = min_delay

            # Pulse the step pin to move one step
            self.step_pin.value(1)
            self.step_pin.value(0)
            time.sleep_us(int(current_delay))

        # If an overshoot was requested, reverse direction to move back the extra steps.
        if overshoot > 0:
            self.dir_pin.value(0 if move_direction == 1 else 1)
            time.sleep(0.05)  # Brief pause before reversing
            for _ in range(overshoot):
                self.step_pin.value(1)
                self.step_pin.value(0)
                time.sleep_us(int(min_delay))

        # Update the internal position state
        self.position = target_position

    def get_position(self):
        """Return the current position in steps."""
        return self.position

    def Run(self, target_position, initial_delay=1000, min_delay=300, overshoot=0):
        """
        Convenience method to move the motor to a target position using default speed settings.
        
        Parameters:
            target_position (int): The desired position in steps.
            initial_delay (int): Delay in microseconds at the start/finish.
            min_delay (int): Minimum delay in microseconds between steps.
            overshoot (int): Extra steps to overshoot before reversing.
        """
        self.move_to(target_position, initial_delay, min_delay, overshoot)


# Test function and main code run
if __name__ == '__main__':
    # Example: Initialize the stepper motor with direction, step, and microstepping pins.
    # Adjust the pin numbers and modes as needed for your hardware.
    test = Stepper(Pin(2, Pin.OUT), Pin(5, Pin.OUT), Pin(15, Pin.OUT))
    
    # Run the motor to position 0 using the default parameters.
    test.Run(0)
    
    # Main loop doing other tasks
    while True:
        print('meanwhile...')
        time.sleep(1)
