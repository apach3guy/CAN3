#!/usr/bin/python3

import can
import os

#Global Variables
frame_counter = 0
MAX_NUMBER_OF_FRAMES = 6000

print('Content-type: text/html\n\n')

os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
dev = can.interface.Bus(channel='can0', bustype='socketcan_native')
  
volts = []
temp = []

#Run through the capture loop until the maximum number of frames is reached
while frame_counter <= MAX_NUMBER_OF_FRAMES:
    frame_counter = frame_counter + 1
    message = dev.recv()
    
	#ID6F2
    if message.arbitration_id == 1778:
        if message.data[0] == 0 or len(volts) != 0:
            d1 = (message.data[1] | ((message.data[2] & 0x03F)<<8))
            d2 = ((message.data[2]>>6) | ((message.data[3]<<2) | ((message.data[4] & 0xF)<<10)))
            d3 = ((message.data[4]>>4) | ((message.data[5]<<4) | ((message.data[6] & 3)<<12)))
            d4 = ((message.data[6]>>2) | ((message.data[7])<<6))
            if message.data[0] < 24:
                volts.append(round(d1 * 0.000305, 3))
                volts.append(round(d2 * 0.000305, 3))
                volts.append(round(d3 * 0.000305, 3))
                volts.append(round(d4 * 0.000305, 3))
            else:
                temp.append(round(d1 * 0.0122, 3))
                temp.append(round(d2 * 0.0122, 3))
                temp.append(round(d3 * 0.0122, 3))
                temp.append(round(d4 * 0.0122, 3))
            if message.data[0] == 31:
                break
# i = 0
# while i < len(volts):
    # print("Brick " + str(i) + " " + str(volts[i]))
    # i += 1
l_volts = len(volts)
l_temp = len(temp)

i = 0
n = 1
while i < l_volts:
    if (i % 6 == 0 and i + 1 != l_volts):
        print("<br><b>Module " + str(n) + "</b>")
        n += 1
    print(str(volts[i]) + " V ")
    i += 1
print("<p>Average: " + str(round((sum(volts) / len(volts)), 2)))
print("Min: " + str(min(volts)))
print("Max: " + str(max(volts)))
print("<hr>")

i = 0
n = 1
while i < l_temp:
    if (i % 2 == 0 and i + 1 != l_temp):
        print("<br><b>Module " + str(n) + "</b>")
        n += 1
    print(str(temp[i]) + " C ")
    i += 1
print("<p>Average: " + str(round((sum(temp) / len(temp)), 2)))
print("Min: " + str(min(temp)))
print("Max: " + str(max(temp)))

os.system("sudo /sbin/ip link set can0 down")