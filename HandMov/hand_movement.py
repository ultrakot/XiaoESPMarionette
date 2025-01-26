#movment based on library
from tmc.TMC_2209_StepperDriver import *
from machine import Pin, UART, Timer
import json
import time


# use your pins for pin_step, pin_dir, pin_en here
tmc = TMC_2209(4, 3)
tmc.setLoglevel(Loglevel.info)
#-----------------------------------------------------------------------
# these functions read and print the current settings in the TMC register
#-----------------------------------------------------------------------
tmc.readIOIN()
tmc.readCHOPCONF()
tmc.readDRVSTATUS()
tmc.readGCONF()
#-----------------------------------------------------------------------
# set the Accerleration and maximal Speed
#-----------------------------------------------------------------------
tmc.setAcceleration(2000)
tmc.setMaxSpeed(500)
#-----------------------------------------------------------------------
# activate the motor current output
#-----------------------------------------------------------------------
tmc.setMotorEnabled(True) #enable motor (still not run it) 

tmc.setStallguard_Callback(5, 50, my_callback) # after this function call, StallGuard is active
#connect through UART inside of library
#what to do after stall guard is reached
finishedsuccessfully = tmc.runToPositionSteps(-100, MovementAbsRel.relative)    #move 4000 steps forward
#set position of limit 
if(finishedsuccessfully == True):
    print("Movement finished successfully")
else:
    print("Movement was not completed")

#change direction and does this again 

#----------------------------------------------------------------------
# set all position and toggle buttons
#----------------------------------------------------------------------
# Limit switches
upper_limit = Pin(10, Pin.IN, Pin.PULL_UP)  # D10 - upper limit
lower_limit = Pin(8, Pin.IN, Pin.PULL_UP)   # D8 - lower limit
        
# Register position button
register_pos = Pin(9, Pin.IN, Pin.PULL_UP)  # D9 - register position
        
# Movement buttons
move_up = Pin(1, Pin.IN, Pin.PULL_UP)      # D1 - step up
move_down = Pin(2, Pin.IN, Pin.PULL_UP)    # D2 - step down
        
# Toggle switch
toggle = Pin(0, Pin.IN, Pin.PULL_UP)       # D0 - toggle mode
#-----------------------------------------------------------------------

# System state
current_position = 0
is_moving = False
last_button_time = 0
debounce_ms = 50  # 50ms debounce time

        
# Set up interrupts for buttons
upper_limit.irq(trigger=Pin.IRQ_FALLING, handler=handle_upper_limit)
lower_limit.irq(trigger=Pin.IRQ_FALLING, handler=handle_lower_limit)
register_pos.irq(trigger=Pin.IRQ_FALLING, handler=handle_register)
move_up.irq(trigger=Pin.IRQ_FALLING, handler=handle_move_up)
move_down.irq(trigger=Pin.IRQ_FALLING, handler=handle_move_down)
toggle.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_toggle)

def handle_upper_limit(self, pin):
    if not self.debounce():
        return
    print("Upper limit reached")
    #go to lower limit
    if not is_moving:
        tmc.runToPositionSteps(upper_limit, MovementAbsRel.absolute)
    #register position
    #go to upper limit 
    
def handle_lower_limit(self, pin):
    print("Lower limit reached")
    #go to lower limit
    if not is_moving:
        tmc.runToPositionSteps(lower_limit, MovementAbsRel.absolute)

def handle_register(self, pin):
    print("Position registered:", self.current_position)
    #get current position, write it to config file
    if is_moving:
        tmc.stop()
        curren_pos = tmc.getCurrentPosition()
    else
        tmc.runToPositionSteps(curren_pos, MovementAbsRel.absolute) 
 
    
def handle_move_up(self, pin):
    print("Moving up")
    tmc.runToPositionSteps(1)  
    
def handle_move_down(self, pin):
    print("Moving down")
    tmc.runToPositionSteps(-1)
    
def handle_toggle(self, pin):
    #no debounce
    #start proccess of moving the motor 
    toggle_state = pin.value()
    print("Toggle state:", "ON" if toggle_state else "OFF")
    
def my_callback(channel):  
    print("StallGuard!")
    tmc.stop()
      