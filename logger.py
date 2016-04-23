#!/usr/bin/python3
# basic logging to file.

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
SHOW_REAR_POWER_DATA = True
SHOW_FRNT_POWER_DATA = False
SHOW_BATT_DATA = True
LOGGING_ENABLED = False
FILE_NAME = '' #Defaults to current date and time

#Global Variables
frame_counter = 0
MAX_NUMBER_OF_FRAMES = 20000

#Motor/Power Vars
pDiss = 0.0
mechPower = 0.0
statorCurr = 0.0
torqMeas = 0.0
torqEst = 0.0
pedalPos = 0
speedMPH = 0.0
mtrRPM = 0

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
  file_ = open('../log/' + st + '.csv', 'w')
  print('New File Opened, now logging data. ')

#Run through the capture loop until the maximum number of frames is reached
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
            
        if message.arbitration_id == 1778 and message.data[0] > 23:
            d1 = (message.data[1] | ((message.data[2] & 0x03F)<<8))
            pack_temp = (d1 * 0.0122)

    if SHOW_REAR_POWER_DATA == True:
        if message.arbitration_id == 614:
            #All power units in kW
            # pDiss = message.data[1] * 125
            mechPower = ((message.data[2] + ((message.data[3] & 0x7)<<8))-(512 * (message.data[3] & 0x4))) / 2
            statorCurr = message.data[4] + ((message.data[5] & 0x7)<<8)
        
        if message.arbitration_id == 340:
            #Nm
            torqMeas = (message.data[5] + ((message.data[6] & 0x1F)<<8)-(512 * (message.data[6] & 0x10))) * 0.25
            #percent
            pedalPos = (message.data[2] * 0.4)
        
        #ID116
        if message.arbitration_id == 278:
            speedMPH = ((message.data[2] + ((message.data[3] & 0xF)<<8))-500) / 20
            # torqEst = ((message.data[0] + ((message.data[1] & 0xF)<<8))-(512 * (message.data[1] & 0x8))) / 2
        
        #ID106 
        if message.arbitration_id == 262:
            mtrRPM = (message.data[4] + (message.data[5]<<8))-(512 * (message.data[5]&0x80))

    if WRITE_TO_FILE == True:
        if frame_counter == 1:
            write_data = ("time, msg_id, soc, temp, pedal_pos, pack_volt, pack_current, torque, mechPower, speedMPH\n")
        else:
            write_data = ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (time.time(), hex(message.arbitration_id)[2:], soc_ui, pack_temp, pedalPos, pack_volt, pack_current, torqMeas, mechPower, speedMPH))
        file_.write(write_data)
        
if WRITE_TO_FILE == True:
  file_.close()
  print("File " + st + '.csv closed. ')

os.system("sudo /sbin/ip link set can0 down")
print("Connection Closed")