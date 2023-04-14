'''
Time:2023.3.22
Company:小二极客科技有限公司
Use:Inverse kinematics algorithm for a three link manipulator(三连杆接机械臂逆运动学算法)
'''

import math


def Arm(x = None, y = None):

    pi = 3.14

    # Define the length of each link
    # 定义连杆长度，单位为毫米
    L1 = 105     # L1
    L2 = 100     # L2
    L3 = 120     # L3

    # Define the end-effector position and orientation
    # 定义末端关节的位置为x,y，单位为毫米，姿态为theta（即 L3与X轴的夹角,这里设置为0 ），单位为弧度。这math.radians函数将角度转换为弧度
    if x is None:
        x = int(input("x:"))
    if y is None:
        y = int(input("y:"))
    theta = math.radians(0)

    # Calculate the intermediate position
    # 计算中间位置Bx,By，即第二个关节的位置。这里用三角函数和末端关节的位置和姿态来求解
    Bx = x - L3 * math.cos(theta)
    By = y - L3 * math.sin(theta)

    # Calculate the first and second joint angles using inverse kinematics formula for two-link arm
    # 计算第一个和第二个关节的角度q1,q2，使用二连杆机械臂的逆运动学公式。
    # 这里用math.acos和math.atan2函数来求解反余弦和反正切。使用math.sqrt函数求平方根
    lp = Bx**2 + By**2
    alpha = math.atan2(By, Bx)
    tmp = (L1*L1 + lp - L2*L2) / (2*L1*math.sqrt(lp))
    if tmp < -1:
        tmp = -1
    elif tmp > 1:
        tmp = 1
    beta = math.acos(tmp)
    q1 = -(pi/2.0 - alpha - beta)
    tmp = (L1*L1 + L2*L2 - lp) / (2*L1*L2)
    if tmp < -1:
        tmp = -1
    elif tmp > 1:
        tmp = 1
    q2 = math.acos(tmp) - pi

    # Calculate the third joint angle using the end-effector orientation
    # 计算第三个关节的角度q3，使用末端关节的姿态（预先定义，theta）减去前两个角度得到。
    # math.degrees函数将弧度转换为角度
    q3 = - q1 - q2 - pi/2

    # 舵机编号3、4、5控制伸缩姿态,每一个舵机的初始值为2047,与前一个连杆处于同一直线。每一个舵机的取值范围:0~4095,相当于0~360度
    # 计算出舵机相对于前杆的旋转角度后 *11.375转换成舵机的旋转值
    # 由于4、5号舵机连接结构与 3号的不同,
    #    3号:角度为正数 逆时针旋转 数值减小 -- 角度为负数 顺时针旋转 数值增大。
    # 4、5号:角度为正数 逆时针旋转 数值增大 -- 角度为负数 顺时针旋转 数值减小。
    # 所以4、5号舵机需要相加。3号舵机需要相减
    angle_5 = int(2047 + int(math.degrees(q1) * 11.375))
    angle_4 = int(2047 + int(math.degrees(q2) * 11.375))
    angle_3 = int(2047 - int(math.degrees(q3) * 11.375))

    # Print the results in radians and degrees
    # 分别显示弧度和角度。用math.degrees函数将弧度转换为角度
    print("-------------------------")
    print("5 = ", int(math.degrees(q1)))
    print("4 = ", int(math.degrees(q2)))
    print("3 = ", int(math.degrees(q3)))
    print("-------------------------")
    print("angle_5 = ", angle_5)
    print("angle_4 = ", angle_4)
    print("angle_3 = ", angle_3)

    return angle_3,angle_4,angle_5