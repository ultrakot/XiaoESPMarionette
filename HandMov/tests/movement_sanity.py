from machine import Pin
import time 

dir_pin = Pin(1, Pin.OUT)
step_pin = Pin(1, Pin.OUT)
en_pin = Pin(2,Pin.OUT)

en_pin.value(0)
time.sleep_ms(10)

while True:
    step_pin.value(0)
    time.sleep_us(5)
    step_pin.value(1)
    time.sleep_us(5)