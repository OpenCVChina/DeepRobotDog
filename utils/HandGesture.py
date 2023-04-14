import numpy as np
import cv2 as cv


# used to estimate what the handpose is
class HandGesture:
    def __init__(self, detector, estimator):
        self.detector = detector
        self.estimator = estimator

    def estimate(self, image, bbox=None, handedness_thr=0.6):
        if bbox is None:
            bias = np.array([0, 0]).astype(np.int32)  # hand landmarks bias to left-top
        else:
            bias = bbox[0]  # hand landmarks bias to left-top
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]

        self.gestures = np.empty(shape=(0, 1))
        self.hands = np.empty(shape=(0, 132))

        # detect palms
        palms = self.detector.infer(image)
        gestures = np.array([])
        area_list = np.array([])
        # estimate the pose of each hand
        for palm in palms:
            # handpose detector
            handpose = self.estimator.infer(image, palm)
            if handpose is not None:
                handedness = handpose[-2]
                # filter left hands
                if handedness < handedness_thr:
                    continue

                # add bias
                bbox = handpose[0:4].reshape(2, 2)
                handpose[0:4] = (bbox + bias).reshape(-1)
                handpose[4:67].reshape(21, 3)[:, 0:2] += bias

                self.hands = np.vstack((self.hands, handpose))
                landmarks = handpose[4:67].reshape(21, 3)[:, 0:2]
                gestures = np.append(gestures, self.__gesture_classification(landmarks))
                w, h = bbox[1] - bbox[0]
                area_list = np.append(area_list, w * h)
        self.gestures = gestures
        return self.gestures, area_list

    def visualize(self, image, thickness=2):
        for idx, handpose in enumerate(self.hands):
            bbox = handpose[0:4].astype(np.int32)
            landmarks_screen = handpose[4:67].reshape(21, 3).astype(np.int32)

            # draw box
            cv.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), thickness)
            # draw hand label
            if self.gestures[idx] is not None:
                cv.putText(image, '{}'.format(self.gestures[idx]), (bbox[0], bbox[1] + 22 * thickness),
                           cv.FONT_HERSHEY_SIMPLEX, thickness, (0, 0, 255))
            # Draw line between each key points
            landmarks = landmarks_screen[:, 0:2]
            cv.line(image, landmarks[0], landmarks[1], (255, 255, 255), thickness)
            cv.line(image, landmarks[1], landmarks[2], (255, 255, 255), thickness)
            cv.line(image, landmarks[2], landmarks[3], (255, 255, 255), thickness)
            cv.line(image, landmarks[3], landmarks[4], (255, 255, 255), thickness)

            cv.line(image, landmarks[0], landmarks[5], (255, 255, 255), thickness)
            cv.line(image, landmarks[5], landmarks[6], (255, 255, 255), thickness)
            cv.line(image, landmarks[6], landmarks[7], (255, 255, 255), thickness)
            cv.line(image, landmarks[7], landmarks[8], (255, 255, 255), thickness)

            cv.line(image, landmarks[0], landmarks[9], (255, 255, 255), thickness)
            cv.line(image, landmarks[9], landmarks[10], (255, 255, 255), thickness)
            cv.line(image, landmarks[10], landmarks[11], (255, 255, 255), thickness)
            cv.line(image, landmarks[11], landmarks[12], (255, 255, 255), thickness)

            cv.line(image, landmarks[0], landmarks[13], (255, 255, 255), thickness)
            cv.line(image, landmarks[13], landmarks[14], (255, 255, 255), thickness)
            cv.line(image, landmarks[14], landmarks[15], (255, 255, 255), thickness)
            cv.line(image, landmarks[15], landmarks[16], (255, 255, 255), thickness)

            cv.line(image, landmarks[0], landmarks[17], (255, 255, 255), thickness)
            cv.line(image, landmarks[17], landmarks[18], (255, 255, 255), thickness)
            cv.line(image, landmarks[18], landmarks[19], (255, 255, 255), thickness)
            cv.line(image, landmarks[19], landmarks[20], (255, 255, 255), thickness)

            for p in landmarks:
                cv.circle(image, p, thickness, (0, 0, 255), -1)

        return image

    def __vector_2_angle(self, v1, v2):
        uv1 = v1 / np.linalg.norm(v1)
        uv2 = v2 / np.linalg.norm(v2)
        angle = np.degrees(np.arccos(np.dot(uv1, uv2)))
        return angle

    def __hand_angle(self, hand):
        angle_list = []
        # thumb
        angle_ = self.__vector_2_angle(
            np.array([hand[0][0] - hand[2][0], hand[0][1] - hand[2][1]]),
            np.array([hand[3][0] - hand[4][0], hand[3][1] - hand[4][1]])
        )
        angle_list.append(angle_)
        # index
        angle_ = self.__vector_2_angle(
            np.array([hand[0][0] - hand[6][0], hand[0][1] - hand[6][1]]),
            np.array([hand[7][0] - hand[8][0], hand[7][1] - hand[8][1]])
        )
        angle_list.append(angle_)
        # middle
        angle_ = self.__vector_2_angle(
            np.array([hand[0][0] - hand[10][0], hand[0][1] - hand[10][1]]),
            np.array([hand[11][0] - hand[12][0], hand[11][1] - hand[12][1]])
        )
        angle_list.append(angle_)
        # ring
        angle_ = self.__vector_2_angle(
            np.array([hand[0][0] - hand[14][0], hand[0][1] - hand[14][1]]),
            np.array([hand[15][0] - hand[16][0], hand[15][1] - hand[16][1]])
        )
        angle_list.append(angle_)
        # pink
        angle_ = self.__vector_2_angle(
            np.array([hand[0][0] - hand[18][0], hand[0][1] - hand[18][1]]),
            np.array([hand[19][0] - hand[20][0], hand[19][1] - hand[20][1]])
        )
        angle_list.append(angle_)
        return angle_list

    def __finger_status(self, lmList):
        fingerList = []
        originx, originy = lmList[0]
        keypoint_list = [[5, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
        for point in keypoint_list:
            x1, y1 = lmList[point[0]]
            x2, y2 = lmList[point[1]]
            if np.hypot(x2 - originx, y2 - originy) > np.hypot(x1 - originx, y1 - originy):
                fingerList.append(True)
            else:
                fingerList.append(False)

        return fingerList

    def __gesture_classification(self, hand):
        thr_angle = 65.
        thr_angle_thumb = 30.
        thr_angle_s = 49.
        gesture_str = None

        angle_list = self.__hand_angle(hand)
        thumbOpen, firstOpen, secondOpen, thirdOpen, fourthOpen = self.__finger_status(hand)

        # squat
        if (angle_list[0] > thr_angle_thumb) and (angle_list[1] > thr_angle) and (
                angle_list[2] < thr_angle) and (angle_list[3] < thr_angle) and (angle_list[4] < thr_angle) and \
                not firstOpen and secondOpen and thirdOpen and fourthOpen:
            gesture_str = "squat"
        # turning
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (
                angle_list[2] > thr_angle) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle) and \
                firstOpen and not secondOpen and thirdOpen and fourthOpen:
            gesture_str = "turning"
        # twisting
        elif (angle_list[0] < thr_angle_thumb) and (angle_list[1] > thr_angle) and (
                angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle) and \
                thumbOpen and not firstOpen and not secondOpen and not thirdOpen and not fourthOpen:
            gesture_str = "twisting"
        # forward
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (
                angle_list[2] < thr_angle_s) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle) and \
                not thumbOpen and firstOpen and secondOpen and not thirdOpen and not fourthOpen:
            gesture_str = "forward"
        # back
        elif (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (
                angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle_s) and \
                thumbOpen and firstOpen and secondOpen and thirdOpen and fourthOpen:
            gesture_str = "back"
        # stop
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (
                angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle_s) and \
                not thumbOpen and firstOpen and secondOpen and thirdOpen and fourthOpen:
            gesture_str = "stop"
        return gesture_str