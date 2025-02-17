from stepper2130.tmc_spi import TMC2130_SPI
from stepper2130.Stepper import Stepper
from program.button_logic import ButtonControl
import time

def main():
    # Initialize components
    tmc_spi = TMC2130_SPI()
    stepper = Stepper()
    buttons = ButtonControl(stepper, tmc_spi)
    
    # Perform initial homing
    buttons.home()
    
    # Main loop
    while True:
        time.sleep_ms(100)

if __name__ == '__main__':
    main()