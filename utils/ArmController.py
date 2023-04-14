import sys
import os
import time

from utils.RobotArm.scservo_sdk import *  # Uses SCServo SDK library
from utils.RobotArm.three_Inverse_kinematics import Arm

# 舵机编号，抓手为1，底盘为6
SCS_ID_1 = 1  # SCServo ID : 1  抓手开合
SCS_ID_2 = 2  # SCServo ID : 2  抓收旋转
SCS_ID_3 = 3  # SCServo ID : 3  第三连杆
SCS_ID_4 = 4  # SCServo ID : 4  第二连杆
SCS_ID_5 = 5  # SCServo ID : 5  第一连杆
SCS_ID_6 = 6  # SCServo ID : 6  控制整个机械臂旋转

# 舵机旋转角度数值，以2047为中间值
# 由于4、5号舵机连接结构与 3号的不同,
#    3号:角度为正数 逆时针旋转 数值减小 -- 角度为负数 顺时针旋转 数值增大。
# 4、5号:角度为正数 逆时针旋转 数值增大 -- 角度为负数 顺时针旋转 数值减小。
SCS_1_INIT_VALUE = 2400  # 抓手初始状态 闭合。闭合最大数值：2450
SCS_1_STATUS_VALUE = 2047  # 抓手张开。最大张开角度数值：1600；张开-->小    闭合-->大

SCS_2_INIT_VALUE = 2047  # 抓手初始旋转状态
SCS_2_STATUS_VALUE = 2047  # 抓手旋转值，2047中间值水平，大-->逆时针   小-->顺时针 取值范围：0~4095

SCS_3_INIT_VALUE = 3080  # 3关节 初始状态
SCS_3_STATUS_VALUE = 2800  # 3关节 2047中间值与前臂水平，顺-->大   逆-->小  取值范围尽可能在：3060~1060
SCS_3_MOVE_VALUE = 1070  # 运动姿态，使用机械臂上得摄像头
SCS_3_TRANSPORT1_VALUE = 3060  # 运输姿态1：药瓶水平
SCS_3_TRANSPORT2_VALUE = 2940  # 运输姿态2：药瓶垂直

SCS_4_INIT_VALUE = 800  # 4关节 初始状态
SCS_4_STATUS_VALUE = 1100  # 4关节 2047中间值与前臂水平，顺-->小   逆-->大  取值范围尽可能在：1060~3060
SCS_4_MOVE_VALUE = 540  # 运动姿态，使用机械臂上得摄像头
SCS_4_TRANSPORT1_VALUE = 1024  # 运输姿态1：药瓶水平
SCS_4_TRANSPORT2_VALUE = 1430  # 运输姿态2：药瓶垂直

SCS_5_INIT_VALUE = 2400  # 5关节 初始状态
SCS_5_STATUS_VALUE = 3030  # 5关节 2047中间值与前臂水平，顺-->小   逆-->大  取值范围尽可能在：1060~3060
SCS_5_MOVE_VALUE = 1540  # 运动姿态，使用机械臂上得摄像头
SCS_5_TRANSPORT1_VALUE = 2200  # 运输姿态1：药瓶水平
SCS_5_TRANSPORT2_VALUE = 2540  # 运输姿态2：药瓶垂直

SCS_6_INIT_VALUE = 2047  # 机械臂整体旋转初始状态：正前方
SCS_6_STATUS_VALUE = 2047  # 2047中间值，顺时针(右)-->大     逆时针(左)-->小     取值范围：0~4095

SCS_MOVING_SPEED = 1500  # SCServo moving speed 旋转速度
SCS_MOVING_ACC = 50  # SCServo moving acc   旋转加速度

# Default setting
BAUDRATE = 500000  # SCServo default baudrate : 500000. 设置波特率
DEVICENAME = 'COM6'  # Check which port is being used on your controller. 选择串口
# ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

class ArmController:
    def __init__(self, device = 'COM6'):
        DEVICENAME = device
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = sms_sts(self.portHandler)

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")

        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")

    def set_pose(self, mode = 0):
        if mode == 0:  # 初始姿态1   键盘上的 1，不是数字小键盘上的1
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_1, SCS_1_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_2, SCS_2_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_3, SCS_3_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_4, SCS_4_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_5, SCS_5_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_6, SCS_6_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
        elif mode == 1:  # 初始姿态2    键盘上的 2，不是数字小键盘上的2
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_1, SCS_1_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_2, SCS_2_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_3, SCS_3_STATUS_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_4, SCS_4_STATUS_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_5, SCS_5_STATUS_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_6, SCS_6_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
        elif mode == 2:  # 运动姿态     键盘上的 3，不是数字小键盘上的3
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_1, SCS_1_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_2, SCS_2_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_3, SCS_3_MOVE_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            time.sleep(2)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_4, SCS_4_MOVE_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_5, SCS_5_MOVE_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_6, SCS_6_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
        elif mode == 3:  # 运输姿态，药瓶水平   键盘上的 4，不是数字小键盘上的4
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_1, SCS_1_INIT_VALUE, SCS_MOVING_SPEED, SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_2, SCS_2_INIT_VALUE, SCS_MOVING_SPEED, SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_6, SCS_6_INIT_VALUE, SCS_MOVING_SPEED, SCS_MOVING_ACC)
            time.sleep(1)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_5, SCS_5_TRANSPORT1_VALUE, SCS_MOVING_SPEED, SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_4, SCS_4_TRANSPORT1_VALUE, SCS_MOVING_SPEED, SCS_MOVING_ACC)
            time.sleep(1)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_3, SCS_3_TRANSPORT1_VALUE, SCS_MOVING_SPEED, SCS_MOVING_ACC)
        elif mode == 4:  # 运输姿态，药瓶垂直   键盘上的 5，不是数字小键盘上的5
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_1, SCS_1_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_2, SCS_2_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_5, SCS_5_TRANSPORT2_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_4, SCS_4_TRANSPORT2_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_3, SCS_3_TRANSPORT2_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
            scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_6, SCS_6_INIT_VALUE, SCS_MOVING_SPEED,
                                                                  SCS_MOVING_ACC)
    def grap(self, dis, height = 30):
        angle_3, angle_4, angle_5 = Arm(dis, height)
        # 设定三个角度的阈值，避免舵机堵转
        if angle_3 < 1000 or angle_3 > 3200 or angle_4 < 540 or angle_4 > 3400 or angle_5 < 1000 or angle_5 > 3050:
            return False

        # Write SCServo goal position/moving speed/moving acc
        # scs_id：舵机编号  scs_goal_position[]:旋转值   SCS_MOVING_SPEED：旋转速度   SCS_MOVING_ACC：加速度
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_1, SCS_1_STATUS_VALUE, SCS_MOVING_SPEED,
                                                              SCS_MOVING_ACC)
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_2, SCS_2_STATUS_VALUE, SCS_MOVING_SPEED,
                                                              SCS_MOVING_ACC)
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_4, angle_4, SCS_MOVING_SPEED, SCS_MOVING_ACC)
        time.sleep(1)
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_3, angle_3, SCS_MOVING_SPEED, SCS_MOVING_ACC)
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_5, angle_5, SCS_MOVING_SPEED, SCS_MOVING_ACC)
        scs_comm_result, scs_error = self.packetHandler.WritePosEx(SCS_ID_6, SCS_6_STATUS_VALUE, SCS_MOVING_SPEED,
                                                              SCS_MOVING_ACC)

    def finalize(self):
        self.portHandler.closePort()
