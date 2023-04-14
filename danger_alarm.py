import time
import struct
import cv2 as cv
import numpy as np
import threading

from opencv_zoo.models.text_detection_db.db import DB
from opencv_zoo.models.text_recognition_crnn.crnn import CRNN

from utils.DangerSignRecognition import DangerSignRecognition
from utils.Controller import Controller

Develop_Mode = True # True means use computer camera. False means use dog camera
client_address = ("192.168.1.103", 43897)
server_address = ("192.168.1.120", 43893)


global frame
global number
global is_update_number

if __name__ == '__main__':
    sign_detector = DangerSignRecognition()
    controller = Controller(server_address)

    if Develop_Mode:
        cap = cv.VideoCapture(0)
    else:
        cap = cv.VideoCapture("/dev/video0", cv.CAP_V4L2)
        # cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

        stop_heartbeat = False
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

    # Instantiate DB for text detection
    detector = DB(modelPath='./opencv_zoo/models/text_detection_db/text_detection_DB_IC15_resnet18_2021sep.onnx',
                  inputSize=[736, 736],
                  binaryThreshold=0.3,
                  polygonThreshold=0.5,
                  maxCandidates=200,
                  unclipRatio=2.0,
                  backendId=backend,
                  targetId=target)

    # Instantiate CRNN for text recognition
    recognizer = CRNN(modelPath='./opencv_zoo/models/text_recognition_crnn/text_recognition_CRNN_EN_2023feb_fp16.onnx',
                      backendId=backend, targetId=target)

    global frame
    global number
    global is_update_number
    global lock
    frame = None
    is_update_number = True
    number = None
    lock = False
    # 开一个线程用于慢更新电话号码
    def number_update(detector, recognizer):
        global frame
        global number
        while is_update_number:
            if frame is not None:
                number = None
                image = frame.copy()
                image = cv.resize(image, [736, 736])
                # Inference of text detector
                results = detector.infer(image)
                # Inference of text recognizer
                if len(results[0]) and len(results[1]):
                    texts = []
                    for box, score in zip(results[0], results[1]):
                        texts.append(recognizer.infer(image, box.reshape(8)))
                    for text in texts:
                        if text == "119" or text == "120" or text == "110":
                            number = text
                            print(number)
                            time.sleep(1)  # sleep 1s
                            break

    number_update_thread = threading.Thread(target=number_update, args=(detector, recognizer, ))
    number_update_thread.start()
    sign_buffer = [None] * 3


    def disabled_sleep(t):
        global lock
        lock = True
        time.sleep(t)  # need time to turn 360 degrees
        lock = False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        bbox = sign_detector.detect(frame)
        frame = sign_detector.visualize(frame)
        sign = sign_detector.classify(frame)

        sign_buffer.insert(0, sign)
        sign_buffer.pop()

        if sign is not None and number is not None and all(s == sign_buffer[0] for s in sign_buffer) and not lock:
            print("当前标识为 {}, 当前电话号码为 {}".format(sign, number))
            if (sign == "fire" and number == "119") or \
               (sign == "poison" and number == "110") or \
               (sign == "injure" and number == "120"):
                if not Develop_Mode:
                    # TODO: 图文匹配，点头
                    # pack = struct.pack('<3i', 0x21010309, 0, 0)
                    # controller.send(pack)
                    # 等待8s才能继续下一次动作
                    disabled_thread = threading.Thread(target=disabled_sleep, args=(8,))
                    disabled_thread.start()
            else:
                if not Develop_Mode:
                    # TODO: 图文不匹配，摇头
                    # pack = struct.pack('<3i', 0x21010309, 0, 0)
                    # controller.send(pack)
                    # 等待8s才能继续下一次动作
                    disabled_thread = threading.Thread(target=disabled_sleep, args=(8,))
                    disabled_thread.start()

        cv.imshow("Danger Sign Recognition", frame)
        k = cv.waitKey(1)
        if k == 113 or k == 81:  # q or Q to quit
            print("Demo is quiting......")
            if not Develop_Mode:
                controller.drive_dog("squat")
            cap.release()
            cv.destroyWindow("Danger Sign Recognition")
            stop_heartbeat = True
            is_update_number = False
            break
