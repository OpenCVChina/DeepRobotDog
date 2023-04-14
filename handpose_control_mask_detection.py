import cv2 as cv
import numpy as np
import struct
import threading
import time

from opencv_zoo.models.person_detection_mediapipe.mp_persondet import MPPersonDet
from opencv_zoo.models.object_detection_nanodet.nanodet import NanoDet
from opencv_zoo.models.face_detection_yunet.yunet import YuNet
from opencv_zoo.models.palm_detection_mediapipe.mp_palmdet import MPPalmDet
from opencv_zoo.models.handpose_estimation_mediapipe.mp_handpose import MPHandPose

from utils.RoI import RoIHumanDetMP, RoIObjDetNano, RoIFaceDetYuNet
from utils.HandGesture import HandGesture
from utils.Controller import Controller
from utils.ColorDetection import ColorDetection

# global config
client_address = ("192.168.1.103", 43897)
server_address = ("192.168.1.120", 43893)
Develop_Mode = True  # True means use computer camera. False means use dog camera

if __name__ == '__main__':
    # creat a controller
    controller = Controller(server_address)
    stop_heartbeat = False

    # get raw video frame
    if Develop_Mode:
        cap = cv.VideoCapture(0)
    # from Robot Dog
    else:
        cap = cv.VideoCapture("/dev/video0", cv.CAP_V4L2)
        # cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

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

    # try to use CUDA
    if cv.cuda.getCudaEnabledDeviceCount() != 0:
        backend = cv.dnn.DNN_BACKEND_CUDA
        target = cv.dnn.DNN_TARGET_CUDA
    else:
        backend = cv.dnn.DNN_BACKEND_DEFAULT
        target = cv.dnn.DNN_TARGET_CPU
        print('CUDA is not set, will fall back to CPU.')

    # human detector, used to determine where a person is to reduce the area of interest
    human_detector_mp = MPPersonDet(
        modelPath='./opencv_zoo/models/person_detection_mediapipe/person_detection_mediapipe_2023mar.onnx',
        nmsThreshold=0.3,
        scoreThreshold=0.3,  # lower to prevent missing human body
        topK=1,  # just only one person
        backendId=backend,
        targetId=target)
    # nano detector
    human_detector_nano = NanoDet(
        modelPath='./opencv_zoo/models/object_detection_nanodet/object_detection_nanodet_2022nov.onnx',
        prob_threshold=0.5,
        iou_threshold=0.6,
        backend_id=backend,
        target_id=target)
    # face detector
    face_detector = YuNet(modelPath='./opencv_zoo/models/face_detection_yunet/face_detection_yunet_2022mar.onnx',
                          confThreshold=0.6,  # lower to make sure mask face can be detected
                          nmsThreshold=0.3,
                          topK=5000,  # only one face
                          backendId=backend,
                          targetId=target)
    # palm detector
    palm_detector = MPPalmDet(
        modelPath='./opencv_zoo/models/palm_detection_mediapipe/palm_detection_mediapipe_2023feb.onnx',
        nmsThreshold=0.3,
        scoreThreshold=0.4,  # lower to  prevent missing palms
        topK=500,  # maximum 2 palms to make sure right hand can be detected
        backendId=backend,
        targetId=target)
    # handpose detector
    handpose_detector = MPHandPose(
        modelPath='./opencv_zoo/models/handpose_estimation_mediapipe/handpose_estimation_mediapipe_2023feb.onnx',
        confThreshold=0.6,  # higher to prevent mis-estimation
        backendId=backend,
        targetId=target)

    human_RoI_mp = RoIHumanDetMP(human_detector_mp)
    human_RoI_nano = RoIObjDetNano(human_detector_nano)
    face_RoI_yunet = RoIFaceDetYuNet(face_detector)
    hand_gesture = HandGesture(palm_detector, handpose_detector)
    mask_detector = ColorDetection(np.array([86, 28, 141]), np.array([106, 128, 225]))

    # gesture will be recognized only if the gesture is the same 2 times in a row
    gesture_buffer = [None] * 3
    while True:
        ret, frame = cap.read()
        if ret is None or not ret:
            continue

        # detect RoI by human detection
        bbox = human_RoI_mp.detect(frame)
        image = frame
        # find a person by MediaPipe human detection
        if bbox is not None:
            # usually upper body RoI can be gotten
            upper_body_RoI = human_RoI_mp.get_upper_RoI()
            gestures, area_list = hand_gesture.estimate(frame, upper_body_RoI)
            # face_RoI_yunet.detect(frame, upper_body_RoI)
            # face_RoI = face_RoI_yunet.get_face_RoI()
            # mask_detector.detect(frame, face_RoI)
        # if human detection can't find a person, try NanoDet
        else:
            bbox = human_RoI_nano.detect(frame)
            human_RoI = human_RoI_nano.get_human_RoI()
            gestures, area_list = hand_gesture.estimate(frame, human_RoI)
            # face_RoI_yunet.detect(frame, human_RoI)
            # face_RoI = face_RoI_yunet.get_face_RoI()
            # mask_detector.detect(frame, face_RoI)

        # visualize
        image = hand_gesture.visualize(image)
        # image = mask_detector.visualize(image, "mask")

        cv.imshow("Demo", image)
        k = cv.waitKey(1)
        if k == 113 or k == 81:  # q or Q to quit
            print("Demo is quiting......")
            if not Develop_Mode:
                controller.drive_dog("squat")
            cap.release()
            cv.destroyWindow("Demo")
            stop_heartbeat = True
            break

        # control robot dog
        if gestures.shape[0] != 0:
            # only use the biggest area right hand
            idx = area_list.argmax()
            gesture_buffer.insert(0, gestures[idx])
            gesture_buffer.pop()
            # only if the gesture is the same 3 times, the corresponding command will be executed
            if not Develop_Mode or (
                    gesture_buffer[0] is not None and all(ges == gesture_buffer[0] for ges in gesture_buffer)):
                controller.drive_dog(gesture_buffer[0])
