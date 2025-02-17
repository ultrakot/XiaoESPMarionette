# move_positions.py
import time

def move_between_positions(button_control):
    """
    Moves the stepper to the saved position 1, waits 10 seconds, 
    then moves to the saved position 2.
    
    Args:
        button_control: An instance of ButtonControl containing saved positions
                        and a method `go_to_position(target_pos)` to move the stepper.
    """
    # Ensure both positions are available
    if button_control.saved_position1 is None:
        print("Error: Position 1 is not set.")
        return
    if button_control.saved_position2 is None:
        print("Error: Position 2 is not set.")
        return

    # Move to Position 1
    print("Moving to Position 1...")
    button_control.go_to_position(button_control.saved_position1)
    
    # Optionally wait until the move completes before proceeding
    while button_control.stepper.is_moving:
        time.sleep_ms(10)
        
    print("Reached Position 1. Waiting for 10 seconds...")
    time.sleep(10)

    # Move to Position 2
    print("Moving to Position 2...")
    button_control.go_to_position(button_control.saved_position2)
    
    # Wait until the move completes
    while button_control.stepper.is_moving:
        time.sleep_ms(10)
        
    print("Reached Position 2.")
