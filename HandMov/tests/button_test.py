from machine import Pin
import time

# Define button pins
btn_plus = Pin(22, Pin.IN, Pin.PULL_UP)
btn_minus = Pin(21, Pin.IN, Pin.PULL_UP)
btn_pos1 = Pin(23, Pin.IN, Pin.PULL_UP)
btn_pos2 = Pin(16, Pin.IN, Pin.PULL_UP)

print("Press each button to test. Press Ctrl+C to exit.")
print("Buttons should read 1 when not pressed, 0 when pressed")

try:
    while True:
        print("Plus Button (GPIO 22):", btn_plus.value())
        print("Minus Button (GPIO 21):", btn_minus.value())
        print("Position 1 (GPIO 23):", btn_pos1.value())
        print("Position 2 (GPIO 16):", btn_pos2.value())
        print("-" * 40)
        time.sleep(0.5)  # Check every half second
        
except KeyboardInterrupt:
    print("\nTest ended")

# from machine import Pin
# import time
# import unittest
# 
# # Mock classes to simulate hardware
# class MockStepper:
#     def __init__(self):
#         self.current_position = 0
#         self.is_moving = False
#         self.steps_taken = []
#         
#     def single_step(self, direction):
#         self.current_position += (1 if direction else -1)
#         self.steps_taken.append(direction)
#         
#     def move_steps(self, steps, direction):
#         self.is_moving = True
#         for _ in range(steps):
#             self.single_step(direction)
#         self.is_moving = False
# 
# class MockTMC:
#     def __init__(self):
#         self.stall_count = 0
#         
#     def check_stall(self):
#         self.stall_count += 1
#         return self.stall_count >= 5  # Simulate stall after 5 checks
# 
# class TestButtonControl(unittest.TestCase):
#     def setUp(self):
#         self.stepper = MockStepper()
#         self.tmc = MockTMC()
#         self.button_control = ButtonControl(self.stepper, self.tmc)
#         
#     def test_plus_button(self):
#         # Simulate button press
#         self.button_control.btn_plus.value = lambda: 0
#         self.button_control.handle_plus(self.button_control.btn_plus)
#         
#         self.assertEqual(self.stepper.current_position, 1)
#         self.assertEqual(self.stepper.steps_taken[-1], 1)
#         
#     def test_minus_button(self):
#         # Simulate button press
#         self.button_control.btn_minus.value = lambda: 0
#         self.button_control.handle_minus(self.button_control.btn_minus)
#         
#         self.assertEqual(self.stepper.current_position, -1)
#         self.assertEqual(self.stepper.steps_taken[-1], 0)
#         
#     def test_position1_save_and_recall(self):
#         # Move to position 10
#         for _ in range(10):
#             self.button_control.handle_plus(self.button_control.btn_plus)
#             
#         # Simulate long press to save position
#         self.button_control.btn_pos1.value = lambda: 0
#         self.button_control.handle_pos1(self.button_control.btn_pos1)
#         time.sleep(1.1)  # Wait longer than LONG_PRESS_TIME
#         self.button_control.btn_pos1.value = lambda: 1
#         self.button_control.handle_pos1(self.button_control.btn_pos1)
#         
#         # Move away from saved position
#         self.button_control.handle_minus(self.button_control.btn_minus)
#         
#         # Recall position
#         self.button_control.btn_pos1.value = lambda: 0
#         self.button_control.handle_pos1(self.button_control.btn_pos1)
#         self.button_control.btn_pos1.value = lambda: 1
#         self.button_control.handle_pos1(self.button_control.btn_pos1)
#         
#         self.assertEqual(self.stepper.current_position, 10)
#         
#     def test_homing(self):
#         # Test homing sequence
#         self.button_control.home()
#         
#         # Verify that stall detection was checked
#         self.assertTrue(self.tmc.stall_count > 0)
#         
#         # Verify final position is 0
#         self.assertEqual(self.stepper.current_position, 0)
#         
#         # Verify moved positive 100 steps after stall
#         last_hundred_steps = self.stepper.steps_taken[-100:]
#         self.assertTrue(all(step == 1 for step in last_hundred_steps))
# 
# if __name__ == '__main__':
#     # Create test suite
#     suite = unittest.TestSuite()
#     
#     #suite.addTest(TestButtonControl('test_plus_button'))
#     suite.addTest([
#         TestButtonControl('test_plus_button'),
#         TestButtonControl('test_minus_button'),
#         TestButtonControl('test_position1_save_and_recall'),
#         TestButtonControl('test_homing')
#     ])
#     
#     # Run tests
#     runner = unittest.TextTestRunner()
#     runner.run(suite)