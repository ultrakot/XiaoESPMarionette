from tmc.TMC_2209_StepperDriver import *
from machine import Pin, UART, Timer
import json
import time
#silent2209 library - try the one in git
#init the Driver with UART communication + pins 

#D1 button moves up - ++ steps
#D2 buttons move down -- step
#
#D0 start movment - till stall guard - 100 to ||*|| changed direction - start movement - till stall guard -100
#D9 mid - while stepper motor moves, register the point in which it is pressed
#D10 - goes to storred pos 1
#D8 - goes to storred pos 2
print("---")
print("SCRIPT START")
print("---")
#-----------------------------------------------------------------------
# initiate the TMC_2209 class
# use your pins for pin_step, pin_dir, pin_en here
#-----------------------------------------------------------------------
tmc = TMC_2209(4, 3, 0)

tmc.setLoglevel(Loglevel.info)
#-----------------------------------------------------------------------
# these functions change settings in the TMC register
#-----------------------------------------------------------------------
tmc.setDirection_reg(False)
tmc.setVSense(True)
tmc.setCurrent(600)
tmc.setIScaleAnalog(True)
tmc.setInterpolation(True)
tmc.setSpreadCycle(False)
tmc.setMicrosteppingResolution(1)
tmc.setInternalRSense(False)

print("---\n---")

#-----------------------------------------------------------------------
# these functions read and print the current settings in the TMC register
#-----------------------------------------------------------------------
tmc.readIOIN()
tmc.readCHOPCONF()
tmc.readDRVSTATUS()
tmc.readGCONF()

print("---\n---")

#-----------------------------------------------------------------------
# set the Accerleration and maximal Speed
#-----------------------------------------------------------------------
tmc.setAcceleration(2000)
tmc.setMaxSpeed(500)
#-----------------------------------------------------------------------
# activate the motor current output
#-----------------------------------------------------------------------
tmc.setMotorEnabled(True)
#-----------------------------------------------------------------------
# set a callback function for the stallguard interrupt based detection
# 1. param: pin connected to the tmc DIAG output
# 2. param: is the threshold StallGuard
# 3. param: is the callback function (threaded)
# 4. param (optional): min speed threshold (in steptime measured  in  clock  cycles)
#-----------------------------------------------------------------------
def my_callback(channel):  
    print("StallGuard!")
    tmc.stop()

tmc.setStallguard_Callback(13, 50, my_callback) # after this function call, StallGuard is active

finishedsuccessfully = tmc.runToPositionSteps(4000, MovementAbsRel.relative)    #move 4000 steps forward

if(finishedsuccessfully == True):
    print("Movement finished successfully")
else:
    print("Movement was not completed")





#-----------------------------------------------------------------------
# deactivate the motor current output
#-----------------------------------------------------------------------
tmc.setMotorEnabled(False)

print("---\n---")

#-----------------------------------------------------------------------
# deinitiate the TMC_2209 class
#-----------------------------------------------------------------------
del tmc

print("---")
print("SCRIPT FINISHED")
print("---")
