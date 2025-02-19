## 5 buttons basic confguraton of the driver
from machine import Pin
import time

class StepperControl:
    def __init__(self):
        # Pin setup
        self.step_pin = Pin(4, Pin.OUT)
        self.dir_pin = Pin(3, Pin.OUT)
        #-------------------------------        
        
        # Buttons setup
        self.btn_fwd = Pin(1, Pin.IN, Pin.PULL_UP)
        self.btn_bwd = Pin(2, Pin.IN, Pin.PULL_UP)
        self.btn_pos1 = Pin(18, Pin.IN, Pin.PULL_UP)
        self.btn_pos2 = Pin(20, Pin.IN, Pin.PULL_UP)
        self.btn_pos3 = Pin(19, Pin.IN, Pin.PULL_UP)
        
        # Movement parameters
        self.current_position = 0
        self.step_delay = 0.001  # 1ms between steps
        self.saved_positions = {
            1: 1000,   # Position 1: 1000 steps
            2: 2000,   # Position 2: 2000 steps
            3: 3000    # Position 3: 3000 steps
        }

    def make_step(self):
        self.step_pin.on()
        time.sleep_us(100)  # 100 microseconds pulse
        self.step_pin.off()
        time.sleep(self.step_delay)

    def move_steps(self, steps):
        # Set direction
        if steps > 0:
            self.dir_pin.on()
        else:
            self.dir_pin.off()
            
        # Move required steps
        for _ in range(abs(steps)):
            self.make_step()
            if steps > 0:
                self.current_position += 1
            else:
                self.current_position -= 1

    def move_to_position(self, target_position):
        steps_to_move = target_position - self.current_position
        self.move_steps(steps_to_move)

    def check_buttons(self):
        # Forward button
        if not self.btn_fwd.value():
            self.move_steps(100)
            print("moved forward")
            time.sleep(0.1)  # Debounce delay
            
        # Backward button
        if not self.btn_bwd.value():
            self.move_steps(-100)
            print("moved backward")
            time.sleep(0.1)
            
        # Position buttons
        if not self.btn_pos1.value():
            self.move_to_position(self.saved_positions[1])
            print(f"saved position 1: {self.saved_positions[1]}")
            time.sleep(0.1)
            
        if not self.btn_pos2.value():
            self.move_to_position(self.saved_positions[2])
            print(f"saved position 2: {self.saved_positions[2]}")
            time.sleep(0.1)
            
        if not self.btn_pos3.value():
            self.move_to_position(self.saved_positions[3])
            print(f"saved position 3: {self.saved_positions[3]}")
            time.sleep(0.1)

def main():
    stepper = StepperControl()
    while True:
        stepper.check_buttons()
        time.sleep(0.01)

if __name__ == "__main__":
    main()