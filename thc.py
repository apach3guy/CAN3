#!/usr/bin/python3

import can
import os

#Global Variables
frame_counter = 0
MAX_NUMBER_OF_FRAMES = 2000

#THC human decode
THC_batteryHeaterState = "Undefined"
heater_state = []
heater_state.append("Off")
heater_state.append("Startup")
heater_state.append("BAT_IN_HEAT_CK")
heater_state.append("Run")
heater_state.append("Overtemp")
heater_state.append("Suspended")
heater_state.append("Undefined")
heater_state.append("Undefined")

THC_batteryHeaterTemp = 0
THC_batteryHeaterReq = 0

THC_totalPowerConsumedHV = 0
THC_totalPowerConsumed12V = 0
THC_HVPowerLimit = 0
THC_limitedBatteryHeater = 0
THC_limitedCompressor = 0
THC_limitedPtcHeater = 0

print('Content-type: text/html\n\n')

os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
dev = can.interface.Bus(channel='can0', bustype='socketcan_native')

while frame_counter <= MAX_NUMBER_OF_FRAMES:
    frame_counter = frame_counter + 1
    message = dev.recv()
    
	#ID26A
    if message.arbitration_id == 618:
        THC_batteryHeaterTemp = ((message.data[0] + ((message.data[1]&0x7)<<8)) * 0.125) - 40
        THC_batteryHeaterReq = (message.data[1] & 0x8)>>3
        THC_batteryHeaterState = (message.data[2] & 0x70)>>4
        THC_batteryHeaterState_Human = heater_state[THC_batteryHeaterState]
    
    #ID35A
    if message.arbitration_id == 858:
        THC_totalPowerConsumedHV = (message.data[2] + (message.data[3]<<8))
        THC_totalPowerConsumed12V = (message.data[4] + ((message.data[5] & 0xF)<<8))
        THC_HVPowerLimit = (message.data[6] + (message.data[7]<<8)) / 100
        THC_limitedBatteryHeater = (message.data[5] & 0x10)>>4
        THC_limitedCompressor = (message.data[5] & 0x20)>>5
        THC_limitedPtcHeater = (message.data[5] & 0x40)>>6
        
print("Heater Temp (C): " + str(THC_batteryHeaterTemp))
print("<br>Active Heating Target (C): " + str(THC_batteryHeaterReq))
print("<br>Heater State: " + THC_batteryHeaterState_Human)
print("<br>Total consumption HV: " + str(THC_totalPowerConsumedHV))
print("<br>Total consumption 12V: " + str(THC_totalPowerConsumed12V))
print("<br>HV Power Limit: " + str(THC_HVPowerLimit))
print("<br>is limited heating: " + str(THC_limitedBatteryHeater))
print("<br>is limited cooling: " + str(THC_limitedCompressor))
print("<br>is limited PTC: " + str(THC_limitedPtcHeater))

os.system("sudo /sbin/ip link set can0 down")