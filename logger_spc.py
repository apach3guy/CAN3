#!/usr/bin/python3
# extended period logging to file.

print('Content-type: text/html\n\n')

#Main Import
import sys
import glob
import time, datetime
import io
import os
import can

#Logging/Viewing Settings
SHOW_ALL_IDs = False
WRITE_TO_FILE = True
SHOW_BATT_DATA = True
FILE_NAME = '' #Defaults to current date and time

#Global Variables
MAX_NUMBER_OF_FRAMES = 6000
loop_counter = 0
SEC_BETWEEN_LOOP = 15
MAX_LOOPS = 165

#battery data
batt_odo = 0
wh_dis_tot = 0
wh_chrg_tot = 0
soc_ui = 0
nom_energy_remain = 0
exp_energy_remain = 0
ideal_energy_remain = 0
nom_packfull_energy = 0
pack_volt = 0
pack_current = 0
pack_temp = 0

os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
dev = can.interface.Bus(channel='can0', bustype='socketcan_native')

  
if WRITE_TO_FILE == True:
  if FILE_NAME != '':
      st = FILE_NAME
  else:
      st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H.%M.%S')
  file_ = open('../log/' + st + '_bat_health.csv', 'w')
  print('New File Opened, now logging data. ')

#Run through the capture loop
def capture(dev, frame_counter, MAX_NUMBER_OF_FRAMES):
    volts = []
    temp = []
    
    while frame_counter <= MAX_NUMBER_OF_FRAMES:
        frame_counter = frame_counter + 1
        message = dev.recv()
        
        if SHOW_BATT_DATA == True:
                
            #ID 302
            if message.arbitration_id == 770:
                soc_ui = ((message.data[1]>>2) + ((message.data[2] & 0xF)<<6)) / 10
            
            if message.arbitration_id == 258:
                pack_volt = (message.data[0] | (message.data[1]<<8))/100
                # pack_current = (((message.data[2] | (message.data[3]<<8)) - ((message.data[2] | (message.data[3]<<8)) & 0x8000))-10000)/10
                pack_current = (((message.data[2] + ((message.data[3] & 0x3F)<<8)) - ((message.data[3] & 0x40)<<8))-10000)/10
                
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

    write_data = ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (time.time(), soc_ui, pack_volt, pack_current, round((sum(temp) / len(temp)), 2), min(temp), max(temp), round((sum(volts) / len(volts)), 2), min(volts), max(volts)))
    file_.write(write_data)

while loop_counter < MAX_LOOPS:
    print("<br>Loop iteration: " + str(loop_counter))
    loop_counter = loop_counter + 1
    frame_counter = 0
    capture(dev, frame_counter, MAX_NUMBER_OF_FRAMES)
    time.sleep(SEC_BETWEEN_LOOP)

if WRITE_TO_FILE == True:
  file_.close()
  print("File " + st + '.csv closed. ')

os.system("sudo /sbin/ip link set can0 down")
print("Connection Closed")