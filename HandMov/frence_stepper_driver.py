from machine import Pin, PWM, Timer
import time

class Stepper:
    def __init__(self, dir_pin, step_pin):
        """
        Initialize the stepper motor driver.
        
        Parameters:
            dir_pin (Pin): Direction pin.
            step_pin (Pin): Step pin (PWM will be used on this pin).            
        """
        self.dir_pin = dir_pin
        self.step_pin = PWM(step_pin, freq=1000, duty=0)
        

        # Define a timetable of operations.
        # Each tuple is (ms_value, unused, unused, period)
        # You can add more fields as necessary.
        self.time_table = [
            (1, 0, 0, 2000),
            (0, 0, 0, 20000),
            (1, 0, 0, 2000)
        ]
        self.timer = Timer(-1)
        self.index = 0

    def run(self, t=None):
        """
        Timer callback that updates the stepper's PWM 
        based on the timetable.
        
        If there are more steps in the timetable, the timer is reinitialized.
        When complete, the PWM is stopped.
        """
        # Start or continue the PWM output by setting the duty.
        self.step_pin.duty(32)
        print("Tick (us):", time.ticks_us())

        # Check if there is another step in the timetable.
        if self.index < len(self.time_table):
            # Set the microstepping pin value using the timetable.
            ms_value = self.time_table[self.index][0]
            
            
            # Get the period (in milliseconds) from the table.
            period = self.time_table[self.index][3]
            self.index += 1

            # Schedule the next callback after 'period' milliseconds.
            self.timer.init(period=period, mode=Timer.ONE_SHOT, callback=self.run)
        else:
            # Sequence complete: stop PWM output.
            self.step_pin.duty(0)
            print("Sequence complete.")

if __name__ == '__main__':
    # Initialize the Stepper with the proper pins.
    # Adjust the pin numbers and modes as required by your hardware.
    stepper = Stepper(Pin(2, Pin.OUT), Pin(5))
    
    # Start the sequence.
    stepper.run()
    
    # Main loop can continue to run other tasks.
    while True:
        print("meanwhile...")
        time.sleep(1)
