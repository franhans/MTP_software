import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
#from lib_nrf24 import NRF24
#import file_to_bytes
import time
import spidev
import math
import sys
import os

#from TX import transmit
#from RX import receive

GPIO.setup(14, GPIO.OUT)#LED ON_OFF
GPIO.setup(15, GPIO.OUT)#LED TX
GPIO.setup(18, GPIO.OUT)#LED RX
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#ON_OFF
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#TX_RX

GPIO.output(14,GPIO.LOW)
GPIO.output(15,GPIO.LOW)
GPIO.output(18,GPIO.LOW)

while GPIO.input(16) == True:
    time.sleep(0.02)

GPIO.output(14,GPIO.HIGH)#system is ON
print("ON")

if GPIO.input(20): # If SW2 'ON' then module is TX
    GPIO.output(15,GPIO.HIGH)#module is TX
    print("TX")
else: # If SW2 'OFF' then module is RX
    GPIO.output(18,GPIO.HIGH)#module is RX
    print("RX")
 # If SW1 'OFF' system reset

GPIO.output(14,GPIO.LOW)
GPIO.output(15,GPIO.LOW)
GPIO.output(18,GPIO.LOW)
