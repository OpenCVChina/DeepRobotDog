import cv2 as cv
import numpy as np

# used for finding Range Of Interest area by human detection from MediaPipe
class RoIHumanDetMP:
    def __init__(self, detector, min_area = 50 * 50):
        self.detector = detector
        self.min_area = min_area
        self.person = None
        self.image_width = 0
        self.image_height = 0

    def detect(self, image, bbox = None):
        self.person = None
        if bbox is None:
            bias = np.array([0, 0], dtype=np.int32)
        else:
            bias = bbox[0]
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]
        self.image_height, self.image_width = image.shape[:2]
        # find a person
        persons = self.detector.infer(image)
        if len(persons) != 0:
            self.person = persons[0]  # only choose one person
            self.person[:-1] = (self.person[:-1].reshape(-1, 2) + bias).reshape(-1)
        else:
            self.person = None

        return self.person

    def get_face_RoI(self):
        if self.person is None:
            return None
        bbox = self.person[0: 4].reshape(-1, 2).astype(np.int32)
        return self.__refine_bbox(bbox)

    def get_upper_RoI(self):
        person_landmarks = self.person[4:-1].reshape(4, 2)
        shoulder_point = person_landmarks[2]
        upper_body = person_landmarks[3]
        return self.__get_RoI(shoulder_point, upper_body)

    def get_full_RoI(self):
        person_landmarks = self.person[4:-1].reshape(4, 2)
        mid_hip_point = person_landmarks[0]
        full_body = person_landmarks[1]
        return self.__get_RoI(mid_hip_point, full_body)

    def get_head_RoI(self):
        person_landmarks = self.person[4:-1].reshape(4, 2)
        shoulder_point = person_landmarks[2]
        full_body = person_landmarks[1]
        return self.__get_RoI(shoulder_point, full_body)

    def __get_RoI(self, center_p, bound_p):
        if self.person is None:
            return None
        half_side_len = int(np.linalg.norm(bound_p - center_p))
        bbox = np.array([center_p - half_side_len, center_p + half_side_len]).astype(np.int32)
        return self.__refine_bbox(bbox)

    def __refine_bbox(self, bbox):
        # refine bbox
        bbox[:, 0] = np.clip(bbox[:, 0], 0, self.image_width)
        bbox[:, 1] = np.clip(bbox[:, 1], 0, self.image_height)
        w, h = bbox[1] - bbox[0]
        if w <= 0 or h <= 0 or w * h <= self.min_area:
            return None
        else:
            return bbox

# used for finding Range Of Interest area by Nano Detection
class RoIObjDetNano:
    def __init__(self, detector):
        self.detector = detector
        self.person = None
        self.image_width = 0
        self.image_height = 0
        self.letterbox_scale = None

    def detect(self, image, bbox = None):
        self.person = None
        if bbox is None:
            bias = np.array([0, 0], dtype=np.int32)
        else:
            bias = bbox[0]
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]
        self.image_height, self.image_width = image.shape[:2]
        input_blob = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        # Letterbox transformation
        input_blob, self.letterbox_scale = self.__letterbox(input_blob)
        # Inference
        preds = self.detector.infer(input_blob)

        # find person
        for pred in preds:
            classid = pred[-1].astype(np.int32)
            # only need one person
            if self.__classes[classid] == "person":
                self.person = pred
                self.person[:4] = (self.person[:4].reshape(-1, 2) + bias).reshape(-1)
                break
        return self.person

    def get_human_RoI(self):
        if self.person is None:
            return None
        bbox = self.person[:4]
        # bbox
        bbox = self.__unletterbox(bbox).reshape(-1, 2)
        return bbox

    __classes = ('person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
                 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
                 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
                 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
                 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
                 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
                 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
                 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
                 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
                 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
                 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
                 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
                 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush')

    def __letterbox(self, srcimg, target_size=(416, 416)):
        img = srcimg.copy()

        top, left, newh, neww = 0, 0, target_size[0], target_size[1]
        if img.shape[0] != img.shape[1]:
            hw_scale = img.shape[0] / img.shape[1]
            if hw_scale > 1:
                newh, neww = target_size[0], int(target_size[1] / hw_scale)
                img = cv.resize(img, (neww, newh), interpolation=cv.INTER_AREA)
                left = int((target_size[1] - neww) * 0.5)
                img = cv.copyMakeBorder(img, 0, 0, left, target_size[1] - neww - left, cv.BORDER_CONSTANT,
                                        value=0)  # add border
            else:
                newh, neww = int(target_size[0] * hw_scale), target_size[1]
                img = cv.resize(img, (neww, newh), interpolation=cv.INTER_AREA)
                top = int((target_size[0] - newh) * 0.5)
                img = cv.copyMakeBorder(img, top, target_size[0] - newh - top, 0, 0, cv.BORDER_CONSTANT, value=0)
        else:
            img = cv.resize(img, target_size, interpolation=cv.INTER_AREA)

        letterbox_scale = [top, left, newh, neww]
        return img, letterbox_scale

    def __unletterbox(self, bbox):
        ret = bbox.copy()
        top, left, newh, neww = self.letterbox_scale

        if self.image_height == self.image_width:
            ratio = self.image_height / newh
            ret = ret * ratio
            return ret

        ratioh, ratiow = self.image_height / newh, self.image_width / neww
        ret[0] = max((ret[0] - left) * ratiow, 0)
        ret[1] = max((ret[1] - top) * ratioh, 0)
        ret[2] = min((ret[2] - left) * ratiow, self.image_width)
        ret[3] = min((ret[3] - top) * ratioh, self.image_height)

        return ret.astype(np.int32)

class RoIFaceDetYuNet:
    def __init__(self, detector, min_area = 50 * 50):
        self.detector = detector
        self.face = None
        self.min_area = min_area
        self.image_width = 0
        self.image_height = 0


    def detect(self, image, bbox = None):
        self.face = None
        self.image_height, self.image_width, _ = image.shape
        if bbox is None:
            bias = np.array([0, 0], dtype=np.int32)
        else:
            bias = bbox[0]
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]
        # If image too small, YuNet will throw an error
        if image.shape[1] * image.shape[0] <= 8000:
            return self.face

        # Inference
        self.detector.setInputSize([image.shape[1], image.shape[0]])
        try:
            results = self.detector.infer(image)
        except:
            results = None
        if results is not None:
            self.face = results[0] # only select one face
            self.face[2] += self.face[0]
            self.face[3] += self.face[1]
            self.face[:-1] = (self.face[:-1].reshape(-1, 2) + bias).reshape(-1)
        else:
            self.face = None
        return self.face

    def get_face_RoI(self):
        if self.face is None:
            return None
        bbox = self.face[0:4].reshape(2, 2).astype(np.int32)
        return self.__refine_bbox(bbox)

    def __refine_bbox(self, bbox):
        # refine bbox
        bbox[:, 0] = np.clip(bbox[:, 0], 0, self.image_width)
        bbox[:, 1] = np.clip(bbox[:, 1], 0, self.image_height)
        w, h = bbox[1] - bbox[0]
        if w <= 0 or h <= 0 or w * h <= self.min_area:
            return None
        else:
            return bbox

# TODO: can add other RoI methods, like use yolox
class RoIObjDetYoloX:
    def __init__(self, detector):
        self.detector = detector

