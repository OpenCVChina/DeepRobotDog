#!/usr/bin/env python
#
# *********     Sync Read and Sync Write Example      *********
#
#
# Available SCServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(STS/SMS), and an URT
#

import sys
import os
import time

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

sys.path.append("..")
from scservo_sdk import *                   # Uses SCServo SDK library

# Control table address

# Default setting
BAUDRATE                    = 1000000           # SCServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

SCS_MINIMUM_POSITION_VALUE  = 0             # SCServo will rotate between this value
SCS_MAXIMUM_POSITION_VALUE  = 4095              
SCS_MOVING_SPEED            = 2400          # SCServo moving speed
SCS_MOVING_ACC              = 50            # SCServo moving acc

index = 0
scs_goal_position = [SCS_MINIMUM_POSITION_VALUE, SCS_MAXIMUM_POSITION_VALUE]         # Goal position

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Get methods and members of Protocol
packetHandler = sms_sts(portHandler)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

groupSyncRead = GroupSyncRead(packetHandler, SMS_STS_PRESENT_POSITION_L, 11)

while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    for scs_id in range(1, 11):
        # Add SCServo#1~10 goal position\moving speed\moving accc value to the Syncwrite parameter storage
        scs_addparam_result = packetHandler.SyncWritePosEx(scs_id, scs_goal_position[index], SCS_MOVING_SPEED, SCS_MOVING_ACC)
        if scs_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % scs_id)

    # Syncwrite goal position
    scs_comm_result = packetHandler.groupSyncWrite.txPacket()
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))

    # Clear syncwrite parameter storage
    packetHandler.groupSyncWrite.clearParam()
    time.sleep(0.002) #wait for servo status moving=1
    while 1:
        # Add parameter storage for SCServo#1~10 present position value
        for scs_id in range(1, 11):
            scs_addparam_result = groupSyncRead.addParam(scs_id)
            if scs_addparam_result != True:
                print("[ID:%03d] groupSyncRead addparam failed" % scs_id)

        scs_comm_result = groupSyncRead.txRxPacket()
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(scs_comm_result))

        scs_last_moving = 0;
        for scs_id in range(1, 11):
            # Check if groupsyncread data of SCServo#1~10 is available
            scs_data_result, scs_error = groupSyncRead.isAvailable(scs_id, SMS_STS_PRESENT_POSITION_L, 11)
            if scs_data_result == True:
                # Get SCServo#scs_id present position moving value
                scs_present_position = groupSyncRead.getData(scs_id, SMS_STS_PRESENT_POSITION_L, 2)
                scs_present_speed = groupSyncRead.getData(scs_id, SMS_STS_PRESENT_SPEED_L, 2)
                scs_present_moving = groupSyncRead.getData(scs_id, SMS_STS_MOVING, 1)
                # print(scs_present_moving)
                print("[ID:%03d] PresPos:%d PresSpd:%d" % (scs_id, scs_present_position, packetHandler.scs_tohost(scs_present_speed, 15)))
                if scs_present_moving==1:
                    scs_last_moving = 1;
            else:
                print("[ID:%03d] groupSyncRead getdata failed" % scs_id)
                continue
            if scs_error:
                print(packetHandler.getRxPacketError(scs_error))            
        print("---")

        # Clear syncread parameter storage
        groupSyncRead.clearParam()
        if scs_last_moving==0:
            break
    # Change goal position
    if index == 0:
        index = 1
    else:
        index = 0

# Close port
portHandler.closePort()
