import numpy as np
import cv2 as cv
import threading
import struct
import time

from utils.ColorDetection import ColorDetection
from utils.Controller import Controller
from utils.ArmController import ArmController

# global config
client_address = ("192.168.1.103", 43897)
server_address = ("192.168.1.120", 43893)
Develop_Mode = False  # True means use computer camera. False means use dog camera
if Develop_Mode:
    dog_cam_mtx = np.array([[667.4919, 0., 335.3685], [0., 649.2633, 240.9659], [0., 0., 1.]])  # 相机内参矩阵
    dog_cam_dist = np.array([0.0246, -0.5534, 0.0011, 0.0163, 4.477])  # 畸变系数
else:
    dog_cam_mtx = np.array([[387.1997, 0., 316.7788], [0., 386.6192, 239.7338], [0., 0., 1.]])  # 相机内参矩阵
    dog_cam_dist = np.array([-0.0261, 0.0158, 0.0016, 0.0021, -0.0021])  # 畸变系数

arm_cam_mtx = np.array([[388.1454, 0., 329.4121], [0., 387.7497, 223.481], [0., 0., 1.]])  # 机械臂相机内参矩阵
arm_cam_dist = np.array([-0.1571, -0.218, -0.0024, -0.0011, 0.2089])  # 机械臂相机畸变系数

lower_color = np.array([0, 124, 198])  # 目标药瓶最低hsv色值
upper_color = np.array([19, 225, 255])  # 目标药瓶最高hsv色值
bottle_real_width = 5  # 药瓶的实际宽度为5cm

arcode_mode = cv.aruco.DICT_4X4_50  # 用于定位的ar码的规格，有多种规格
marker_size = 10  # aruco码的实际尺寸是10厘米
left_right_thr = 10  # 左右调整位置时，可容忍的偏差 [-thr, thr] 像素
forward_thr = 30  # 直走时，目标偏差超过thr像素时，开始调整左右位置
target_id = 1  # 目标ar码的值为多少
ar_distance = 20  # 距离ar码多少cm时停下

if __name__ == '__main__':
    global stop_heartbeat
    stop_heartbeat = False

    # 创建一个aruco字典
    dictionary = cv.aruco.getPredefinedDictionary(arcode_mode)
    # creat a controller
    controller = Controller(server_address)
    bottle_detector = ColorDetection(lower_color, upper_color)

    # get raw video frame
    if Develop_Mode:
        dog_cam = cv.VideoCapture(0)
        # arm_controller = ArmController("COM4")
        # arm_controller.set_pose(2)
    # from Robot Dog
    else:
        dog_cam = cv.VideoCapture("/dev/video0", cv.CAP_V4L2)
        arm_controller = ArmController("/dev/ttyUSB0")
        arm_controller.set_pose(3)


        # start to exchange heartbeat pack
        def heart_exchange(con):
            pack = struct.pack('<3i', 0x21040001, 0, 0)
            while True:
                if stop_heartbeat:
                    return
                con.send(pack)
                time.sleep(0.25)  # 4Hz


        heart_exchange_thread = threading.Thread(target=heart_exchange, args=(controller,))
        heart_exchange_thread.start()

        # stand up
        print("Wait 10 seconds and stand up......")
        pack = struct.pack('<3i', 0x21010202, 0, 0)
        controller.send(pack)
        time.sleep(5)
        controller.send(pack)
        time.sleep(5)
        controller.send(pack)
        print("Dog should stand up, otherwise press 'ctrl + c' and re-run the demo")

    # 等待开始
    print("Press 'Y' or 'y' to start...")
    is_running = True  # 是否正在运行
    while is_running:
        ret, frame = dog_cam.read()
        k = cv.waitKey(1)
        if k == 89 or k == 121:  # y or Y to start
            print("start to forward")
            break
        if k == 113 or k == 81:  # q or Q to quit
            print("Demo is quiting......")
            if not Develop_Mode:
                controller.drive_dog("squat")
            dog_cam.release()
            cv.destroyWindow("camera")
            stop_heartbeat = True
            is_running = False
            break
        if not ret:
            continue
        cv.imshow("camera", frame)

    # 找到二维码，并走过去
    center_x = dog_cam.get(cv.CAP_PROP_FRAME_WIDTH) / 2
    center_y = dog_cam.get(cv.CAP_PROP_FRAME_HEIGHT) / 2
    drive_left_right = True
    drive_forward = False
    while is_running and (drive_left_right or drive_forward):
        ret, frame = dog_cam.read()
        k = cv.waitKey(1)
        if k == 113 or k == 81:  # q or Q to quit
            print("Demo is quiting......")
            if not Develop_Mode:
                controller.drive_dog("squat")
            dog_cam.release()
            cv.destroyWindow("camera")
            stop_heartbeat = True
            is_running = False
            break
        if not ret:
            continue

        # 检测aruco码
        arcode_detector = cv.aruco.ArucoDetector(dictionary)
        corners, ids, rejected = arcode_detector.detectMarkers(frame)
        # 估计aruco码的姿态
        marker_points = np.array([[-marker_size / 2, marker_size / 2, 0],
                                  [marker_size / 2, marker_size / 2, 0],
                                  [marker_size / 2, -marker_size / 2, 0],
                                  [-marker_size / 2, -marker_size / 2, 0]], dtype=np.float32)

        distance_list = []
        for c in corners:
            _, rvec, tvec = cv.solvePnP(marker_points, c, dog_cam_mtx, dog_cam_dist, False, cv.SOLVEPNP_IPPE_SQUARE)
            R, _ = cv.Rodrigues(rvec)
            cam_tvec = -R.T @ tvec
            distance_list.append(np.linalg.norm(cam_tvec))
        # 遍历每个aruco码
        if ids is None:
            continue
        if Develop_Mode:
            cv.aruco.drawDetectedMarkers(frame, corners, ids)
        cv.imshow("camera", frame)

        distance = None
        for i in range(len(ids)):
            if ids[i] == target_id:
                # 计算并输出距离
                distance = distance_list[i]
                aruco_center_x = corners[i].mean(axis=1)[0][0]
                break

        if distance is not None:
            diff_x = aruco_center_x - center_x

            # 控制机器狗向前走
            if drive_forward:
                # 左右偏差超出阈值
                if diff_x > forward_thr or diff_x < -forward_thr:
                    drive_left_right = True
                    drive_forward = False
                    controller.drive_dog("stop")
                # 左右偏差在阈值内，只考虑前后
                else:
                    # 距离箱子的距离达到阈值时停下
                    print("ArUco code distance: {:.2f} cm".format(distance))
                    if distance <= ar_distance:
                        print("Arrived!!")
                        controller.drive_dog("stop")
                        dog_cam.release()
                        cv.destroyWindow("camera")
                        drive_forward = False
                    else:
                        controller.drive_dog("forward", 8000)

            if drive_left_right:
                if diff_x > left_right_thr:
                    controller.drive_dog("right", 15000)
                elif diff_x < - left_right_thr:
                    controller.drive_dog("left", 15000)
                else:
                    controller.drive_dog("stop")
                    drive_left_right = False
                    drive_forward = True
    time.sleep(5)

    # 使用机械臂抓取物体
    # get raw video frame
    if Develop_Mode:
        arm_cam = cv.VideoCapture(1)
        # cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    # from Robot Dog
    else:
        arm_controller.set_pose(2)
        print("waiting 5s...")
        time.sleep(5)
        arm_cam = cv.VideoCapture("/dev/video4", cv.CAP_V4L2)
        # cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    # 20次取平均作为最终距离
    seq = [None] * 20
    while is_running:
        k = cv.waitKey(1)
        if k == 113 or k == 81:  # q or Q to quit
            print("Demo is quiting......")
            if not Develop_Mode:
                controller.drive_dog("squat")
            arm_cam.release()
            stop_heartbeat = True
            is_running = False
            break
        ret, frame = arm_cam.read()
        if not ret:
            continue
        # 消除摄像机畸变
        frame = cv.undistort(frame, arm_cam_mtx, arm_cam_dist)
        bbox = bottle_detector.detect(frame)
        if bbox is not None:
            cv.rectangle(frame, bbox[0], bbox[1], (0, 255, 0))
            pixels = bbox[1][0] - bbox[0][0]
            target_distance = bottle_real_width * arm_cam_mtx[0][0] / pixels
            print("distance: {:.4f}cm".format(target_distance))
            seq.insert(0, target_distance)
            seq.pop()
            if not any(x is None for x in seq):
                final_dis = sum(seq) / len(seq)
                print("机械臂视觉距离：", final_dis)
                print("开始抓取")
                final_dis += 14  # 加14cm调整实际位置
                arm_controller.grap(final_dis * 10, 25)  # 相对舵机的距离和高度
                time.sleep(3)
                arm_controller.set_pose(3)
                print("抓取结束")
                arm_cam.release()
                cv.destroyAllWindows()
                arm_controller.finalize()
                is_running = False
                if not Develop_Mode:
                    controller.drive_dog("squat")
                stop_heartbeat = True
        cv.imshow("camera", frame)
