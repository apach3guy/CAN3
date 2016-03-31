#!/usr/bin/python3
# outputs a bunch of bms parameters

import can
import os

#Global Variables
frame_counter = 0
MAX_NUMBER_OF_FRAMES = 2000

# battery data
batt_odo = 0
wh_dis_tot = 0
wh_chrg_tot = 0
soc_ui = 0
nom_energy_remain = 0
exp_energy_remain = 0
ideal_energy_remain = 0
nom_packfull_energy = 0
energy_buffer = 0
pack_volt = 0
energy_till_chargedone = 0
maxDischarge = 0
maxRegen = 0

print('Content-type: text/html\n\n')

os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
dev = can.interface.Bus(channel='can0', bustype='socketcan_native')

while frame_counter <= MAX_NUMBER_OF_FRAMES:
    frame_counter = frame_counter + 1
    message = dev.recv()
    
	#ID382
    if message.arbitration_id == 898:
        nom_energy_remain = ((message.data[1]>>2) + ((message.data[2] & 0x0F) * 64)) * 0.1
        exp_energy_remain = ((message.data[2]>>4) + ((message.data[3] & 0x3F) * 16)) * 0.1
        ideal_energy_remain = ((message.data[3]>>6) + ((message.data[4] & 0xFF) * 4)) * 0.1
        nom_packfull_energy = (message.data[0] + ((message.data[1] & 0x03)<<8)) * 0.1
        energy_till_chargedone = (message.data[5] + ((message.data[6] & 0x03)<<8)) * 0.1
        energy_buffer = ((message.data[6]>>2) + ((message.data[7] & 0x03) * 64)) * 0.1
	
	#ID302
    if message.arbitration_id == 770:
        soc_ui = ((message.data[1]>>2) + ((message.data[2] & 0xF)<<6)) / 10
	
	#ID562
    # if message.arbitration_id == 1378:
        # batt_odo = (message.data[0] + (message.data[1]<<8) + (message.data[2]<<16) + (message.data[3]<<24))/1000
        # ids += 1
	
	#ID102
    # if message.arbitration_id == 546:
        # pack_volt = '%.2f' %(float((message.data[3]*256.0 + message.data[2])/100.0))
        
    #ID
    if message.arbitration_id == 258:
        pack_volt = (message.data[0] | (message.data[1]<<8))/100
        pack_current = (((message.data[2] | (message.data[3]<<8)) & 0x7FFF))/10 # todo: implement sign bit 6 of byte 3? (message.data[3] & 0x20)
        
    #ID232
    if message.arbitration_id == 562:
        maxDischarge = (message.data[2] + (message.data[3]<<8))/100
        maxRegen = (message.data[0] + (message.data[1]<<8))/100

print("Nom Pack Full Energy (kWh): " + str(nom_packfull_energy))
print("<br>Nom Energy Remain (kWh): " + str(nom_energy_remain))
print("<br>Expected Energy Remain (kWh): " + str(exp_energy_remain))
print("<br>Ideal Energy Remain (kWh): " + str(ideal_energy_remain))
print("<br>Energy to Charge Comp (kWh): " + str(energy_till_chargedone))
print("<br>Energy buffer (kWh): " + str(energy_buffer))
print("<p>SoC UI (%): " + str(soc_ui))
print("<br>Max Discharge (kW): " + str(maxDischarge))
print("<br>Max Regen (kW): " + str(maxRegen))
print("<br>Pack Voltage: " + str(pack_volt))
print("<br>Pack Current: " + str(pack_current))
os.system("sudo /sbin/ip link set can0 down")