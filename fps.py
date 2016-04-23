#!/usr/bin/python3

#Global Variables
frame_counter = 0
MAX_NUMBER_OF_FRAMES = 10000

import RPi.GPIO as GPIO
import can
import time, datetime
import os

led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)

# Bring up can0 interface at 500kbps
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
dev = can.interface.Bus(channel='can0', bustype='socketcan_native')

print('Content-type: text/html\n\n')
startTime = datetime.datetime.now()

while frame_counter <= MAX_NUMBER_OF_FRAMES:
    frame_counter = frame_counter + 1
    message = dev.recv()
    print(str(message.arbitration_id) + "<br>")

print ("10,000 frames in " + str(datetime.datetime.now() - startTime))

GPIO.output(led,False)
os.system("sudo /sbin/ip link set can0 down")