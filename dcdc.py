#!/usr/bin/python3

import can
import os

#Global Variables
frame_counter = 0
MAX_NUMBER_OF_FRAMES = 2000

#DC-to-DC vars
inletTemperature = 0
inputPower = 0
outputCurrent = 0
outputPower = 0
outputVoltage = 0

print('Content-type: text/html\n\n')

os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
dev = can.interface.Bus(channel='can0', bustype='socketcan_native')

while frame_counter <= MAX_NUMBER_OF_FRAMES:
    frame_counter = frame_counter + 1
    message = dev.recv()
    
	#ID0210
    if message.arbitration_id == 528:
        inputPower = message.data[3] * 16
        outputCurrent = message.data[4]
        outputVoltage = message.data[5] / 10
        inletTemperature = (((message.data[2] - (2 * (message.data[2] & 0x80))) * 0.5) + 40)
        outputPower = message.data[4] * (message.data[5] / 10)
        
print("Input (W): " + str(inputPower))
print("<br>Output (A): " + str(outputCurrent))
print("<br>Output (V): " + str(outputVoltage))
print("<br>Output (W): " + str(outputPower))
print("<br>Temp (C): " + str(inletTemperature))

os.system("sudo /sbin/ip link set can0 down")