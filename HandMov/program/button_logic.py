from machine import Pin
import time
import json  # Use ujson if needed

class ButtonControl:
    def __init__(self, stepper, tmc_spi):
        # Store references to stepper and SPI
        self.stepper = stepper
        self.tmc_spi = tmc_spi
        
        # Button pins with pullup
        self.btn_plus = Pin(22, Pin.IN, Pin.PULL_UP)
        self.btn_minus = Pin(21, Pin.IN, Pin.PULL_UP)
        self.btn_pos1 = Pin(23, Pin.IN, Pin.PULL_UP)
        self.btn_pos2 = Pin(16, Pin.IN, Pin.PULL_UP)
        
        # State variables
        self.saved_position1 = None
        self.saved_position2 = None
        self.button_press_time = 0
        self.LONG_PRESS_TIME = 1000  # 1 second

        # Load saved positions from file if available
        self.load_positions()
        
        # Configure button interrupts
        self.btn_plus.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
                         handler=self.handle_plus)
        self.btn_minus.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
                          handler=self.handle_minus)
        self.btn_pos1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
                         handler=self.handle_pos1)
        self.btn_pos2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
                         handler=self.handle_pos2)
    
    def load_positions(self):
        """Load saved positions from position.json file."""
        try:
            with open('position.json', 'r') as f:
                data = json.load(f)
                self.saved_position1 = data.get('pos1', None)
                self.saved_position2 = data.get('pos2', None)
                print(f"Loaded positions: pos1={self.saved_position1}, pos2={self.saved_position2}")
        except Exception as e:
            print("Could not load positions:", e)
    
    def save_positions(self):
        """Save current positions to position.json file."""
        data = {
            'pos1': self.saved_position1,
            'pos2': self.saved_position2
        }
        try:
            with open('position.json', 'w') as f:
                json.dump(data, f)
                print("Positions saved to file.")
        except Exception as e:
            print("Error saving positions:", e)
    
    def handle_plus(self, pin):
        """Handle plus button press/release"""
        if not pin.value():  # Button pressed
            #self.stepper.single_step(1)
            self.stepper.move_steps(1000,1)
            print("+ step")
    
    def handle_minus(self, pin):
        """Handle minus button press/release"""
        if not pin.value():  # Button pressed
            #self.stepper.single_step(0)
            self.stepper.move_steps(1000,0)
            print("- step")
    
    def handle_pos1(self, pin):
        """Handle position 1 button"""
        if pin.value() == 0:  # Button pressed
            self.button_press_time = time.ticks_ms()
        else:  # Button released
            press_duration = time.ticks_diff(time.ticks_ms(), self.button_press_time)
            if press_duration > self.LONG_PRESS_TIME:
                self.saved_position1 = self.stepper.current_position
                self.save_positions()  # Update file when saving a new position
                print(f"Position 1 saved: {self.saved_position1}")
            elif self.saved_position1 is not None:
                self.go_to_position(self.saved_position1)
                print("Goes to position 1")
    
    def handle_pos2(self, pin):
        """Handle position 2 button"""
        if pin.value() == 0:  # Button pressed
            self.button_press_time = time.ticks_ms()
        else:  # Button released
            press_duration = time.ticks_diff(time.ticks_ms(), self.button_press_time)
            if press_duration > self.LONG_PRESS_TIME:
                self.saved_position2 = self.stepper.current_position
                self.save_positions()  # Update file when saving a new position
                print(f"Position 2 saved: {self.saved_position2}")
            elif self.saved_position2 is not None:
                self.go_to_position(self.saved_position2)
                print("Goes to position 2")
    
    def go_to_position(self, target_pos):
        """Move to a saved position"""
        if not self.stepper.is_moving:
            steps = target_pos - self.stepper.current_position
            direction = 1 if steps > 0 else 0
            self.stepper.move_steps(abs(steps), direction)
    
    def home(self):
        """Perform homing sequence"""
        print("Starting homing sequence...")
        
        # Move negative until stallGuard triggers
        while not self.tmc_spi.check_stall():
            self.stepper.single_step(0)
            #self.stepper.move_steps(1000,0
            time.sleep_ms(1)
        
        print("Stall detected, moving to home offset...")
        
        # Move 100 steps positive
        self.stepper.move_steps(100, 1)
        
        # Set as zero position
        self.stepper.current_position = 0
        print("Homing complete")


# from machine import Pin
# import time
# 
# class ButtonControl:
#     def __init__(self, stepper, tmc_spi):
#         # Store references to stepper and SPI
#         self.stepper = stepper
#         self.tmc_spi = tmc_spi
#         
#         # Button pins with pullup
#         self.btn_plus = Pin(22, Pin.IN, Pin.PULL_UP)
#         self.btn_minus = Pin(21, Pin.IN, Pin.PULL_UP)
#         self.btn_pos1 = Pin(23, Pin.IN, Pin.PULL_UP)
#         self.btn_pos2 = Pin(16, Pin.IN, Pin.PULL_UP)
#         
#         # State variables
#         self.saved_position1 = None
#         self.saved_position2 = None
#         self.button_press_time = 0
#         self.LONG_PRESS_TIME = 1000  # 1 second
#         
#         # Configure button interrupts
#         self.btn_plus.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
#                          handler=self.handle_plus)
#         self.btn_minus.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
#                           handler=self.handle_minus)
#         self.btn_pos1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
#                          handler=self.handle_pos1)
#         self.btn_pos2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
#                          handler=self.handle_pos2)
#     
#     def handle_plus(self, pin):
#         """Handle plus button press/release"""
#         if not pin.value():  # Button pressed
#             self.stepper.single_step(1)
#             print("+ step")
#     
#     def handle_minus(self, pin):
#         """Handle minus button press/release"""
#         if not pin.value():  # Button pressed
#             self.stepper.single_step(0)
#             print("- step")
#     
#     def handle_pos1(self, pin):
#         """Handle position 1 button"""
#         if pin.value() == 0:  # Button pressed
#             self.button_press_time = time.ticks_ms()
#         else:  # Button released
#             press_duration = time.ticks_diff(time.ticks_ms(), 
#                                            self.button_press_time)
#             if press_duration > self.LONG_PRESS_TIME:
#                 self.saved_position1 = self.stepper.current_position
#                 print(f"Position 1 saved: {self.saved_position1}")
#             elif self.saved_position1 is not None:
#                 self.go_to_position(self.saved_position1)
#                 print("goes to position 1")
#     
#     def handle_pos2(self, pin):
#         """Handle position 2 button"""
#         if pin.value() == 0:  # Button pressed
#             self.button_press_time = time.ticks_ms()
#         else:  # Button released
#             press_duration = time.ticks_diff(time.ticks_ms(), 
#                                            self.button_press_time)
#             if press_duration > self.LONG_PRESS_TIME:
#                 self.saved_position2 = self.stepper.current_position
#                 print(f"Position 2 saved: {self.saved_position2}")
#             elif self.saved_position2 is not None:
#                 self.go_to_position(self.saved_position2)
#                 print("goes to position 2")
#     
#     def go_to_position(self, target_pos):
#         """Move to a saved position"""
#         if not self.stepper.is_moving:
#             steps = target_pos - self.stepper.current_position
#             direction = 1 if steps > 0 else 0
#             self.stepper.move_steps(abs(steps), direction)
#     
#     def home(self):
#         """Perform homing sequence"""
#         print("Starting homing sequence...")
#         
#         # Move negative until stallGuard triggers
#         while not self.tmc_spi.check_stall():
#             self.stepper.single_step(0)
#             time.sleep_ms(1)
#         
#         print("Stall detected, moving to home offset...")
#         
#         # Move 100 steps positive
#         self.stepper.move_steps(100, 1)
#         
#         # Set as zero position
#         self.stepper.current_position = 0
#         print("Homing complete")