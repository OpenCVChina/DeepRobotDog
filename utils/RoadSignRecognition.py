import cv2 as cv
import numpy as np


class RoadSignRecognition:
    def __init__(self, min_area = 50 * 50):
        self.min_area = min_area
        self.image_width = 0
        self.image_height = 0
        self.bbox = None
        self.road_sign = None

    def detect(self, image, bbox = None):
        if bbox is None:
            bias = np.array([0, 0]).astype(np.int32)  # hand landmarks bias to left-top
        else:
            bias = bbox[0]  # hand landmarks bias to left-top
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]
        self.image_height, self.image_width = image.shape[:2]
        self.bbox = None
        # 转换为灰度图像
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # 使用高斯滤波平滑图像
        blur = cv.GaussianBlur(gray, (5, 5), 0)
        # 使用霍夫变换检测圆形
        circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT, 1.2, 100)
        # 如果检测到圆形，绘制边界
        if circles is not None:
            # 将圆形坐标转换为整数
            circles = np.round(circles[0, :]).astype("int")
            # 定义一个阈值，表示两个圆心之间的最大距离，用于判断是否合并
            threshold = 10
            # 定义一个列表，用于存储合并后的圆形
            merged_circles = []
            # 遍历每个圆形
            for (x1, y1, r1) in circles:
                # 定义一个标志，表示当前的圆形是否已经被合并过
                merged = False
                # 遍历已经合并过的圆形列表
                for i in range(len(merged_circles)):
                    # 获取已经合并过的圆形的坐标和半径
                    (x2, y2, r2) = merged_circles[i]
                    # 计算两个圆心之间的距离
                    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    # 如果距离小于阈值，说明两个圆形可以合并
                    if distance < threshold:
                        # 将当前的圆形和已经合并过的圆形进行平均，得到新的圆形
                        if r1 >= r2:
                            merged_circles[i] = (x1, y1, r1)
                        else:
                            merged_circles[i] = (x2, y2, r2)
                        # 设置标志为True，表示当前的圆形已经被合并过
                        merged = True
                        # 跳出循环，不再遍历其他已经合并过的圆形
                        break
                # 如果当前的圆形没有被合并过，就将它添加到已经合并过的圆形列表中
                if not merged:
                    merged_circles.append((x1, y1, r1))
            # 遍历已经合并过的圆形列表，找到最大的圆，作为检测结果
            biggest = None
            biggest_r = -1
            for (x, y, r) in merged_circles:
                if r > biggest_r:
                    biggest = (x, y, r)
                    biggest_r = r
            # 将圆转换成bbox
            if biggest is not None:
                self.bbox = np.array([[biggest[0] - biggest[2], biggest[1] - biggest[2]], [biggest[0] + biggest[2], biggest[1] + biggest[2]]] + bias, np.int32)
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
        [34, 33, 19, 19, 0, 0], # left
    ])

    def classify(self, image):
        self.road_sign = None
        if self.bbox is not None:
            # 图片转换为灰度图
            image = image[self.bbox[0][1]:self.bbox[1][1], self.bbox[0][0]:self.bbox[1][0], :]
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            # 计算作标缩放比例，划分的范围在50*50
            scale = min(self.bbox[1] - self.bbox[0]) / 50
            anchors = self.__class * scale
            anchors = anchors.astype(np.int32)
            if image[anchors[0][1], anchors[0][0]] >= 150 and image[anchors[0][3], anchors[0][2]] >= 150:
                self.road_sign = "turn left"
        else:
            self.road_sign = None
        return self.road_sign

    def visualize(self, image, thickness=1):
        if self.bbox is not None:
            # Draw bounding box on original image (in color)
            cv.rectangle(image, self.bbox[0], self.bbox[1], (0, 255, 0), 2)
            if self.road_sign is not None:
                cv.putText(image, self.road_sign, (self.bbox[0][0], self.bbox[0][1] + 22 * thickness),
                           cv.FONT_HERSHEY_SIMPLEX, thickness, (0, 0, 255))
        return image

