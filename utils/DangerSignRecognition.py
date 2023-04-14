import cv2 as cv
import numpy as np


class DangerSignRecognition:
    def __init__(self, min_area = 50 * 50):
        self.min_area = min_area
        self.image_width = 0
        self.image_height = 0
        self.bbox = None
        self.danger_sign = None

    def detect(self, image, bbox = None):
        if bbox is None:
            bias = np.array([0, 0]).astype(np.int32)  # hand landmarks bias to left-top
        else:
            bias = bbox[0]  # hand landmarks bias to left-top
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]
        self.image_height, self.image_width = image.shape[:2]
        self.bbox = None
        # 转换为灰度图
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # 使用Canny算子进行边缘检测
        edges = cv.Canny(gray, 100, 150)
        # 寻找轮廓
        contours, hierarchy = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # 初始化最大面积和最大轮廓
        max_area = 0
        max_cnt = None
        # 遍历轮廓
        for cnt in contours:
            # 计算轮廓的周长
            perimeter = cv.arcLength(cnt, True)
            # 使用多边形近似轮廓
            approx = cv.approxPolyDP(cnt, 0.02 * perimeter, True)
            # 如果近似轮廓有三个顶点，说明是三角形
            if len(approx) == 3:
                # 计算轮廓的面积
                area = cv.contourArea(cnt)
                # 如果面积大于最大面积，更新最大面积和最大轮廓
                if area > max_area:
                    max_area = area
                    max_cnt = cnt
        # 如果找到了最大轮廓，绘制它并输出bounding box
        if max_cnt is not None and max_area >= self.min_area:
            x, y, w, h = cv.boundingRect(max_cnt)
            self.bbox = np.array([[x, y], [x + w, y + h]] + bias, np.int32)
            return self.__refine_bbox(self.bbox)
        return None


    def __refine_bbox(self, bbox):
        # refine bbox
        bbox[:, 0] = np.clip(bbox[:, 0], 0, self.image_width)
        bbox[:, 1] = np.clip(bbox[:, 1], 0, self.image_height)
        w, h = bbox[1] - bbox[0]
        if w <= 0 or h <= 0 or w * h <= self.min_area:
            return None
        else:
            return bbox
    # x, y, x, y
    __class = np.array([
        [25, 38, 23, 37, 25, 21], # fire
    ])

    def classify(self, image):
        self.danger_sign = None
        if self.bbox is not None:
            # 图片转换为灰度图
            image = image[self.bbox[0][1]:self.bbox[1][1], self.bbox[0][0]:self.bbox[1][0], :]
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            # 计算作标缩放比例，划分的范围在50*50
            scale = (self.bbox[1] - self.bbox[0]) / 50
            anchors = self.__class * np.array([scale, scale, scale]).reshape(-1)
            anchors = anchors.astype(np.int32)
            if image[anchors[0][1], anchors[0][0]] >= 100 and image[anchors[0][3], anchors[0][2]] >= 100 and image[anchors[0][5], anchors[0][4]] < 100:
                self.danger_sign = "fire"
        else:
            self.danger_sign = None
        return self.danger_sign

    def visualize(self, image, thickness=1):
        if self.bbox is not None:
            # Draw bounding box on original image (in color)
            cv.rectangle(image, self.bbox[0], self.bbox[1], (0, 255, 0), 2)
            if self.danger_sign is not None:
                cv.putText(image, self.danger_sign, (self.bbox[0][0], self.bbox[0][1] + 22 * thickness),
                           cv.FONT_HERSHEY_SIMPLEX, thickness, (0, 0, 255))
        return image

