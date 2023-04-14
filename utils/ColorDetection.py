import cv2 as cv
import numpy as np

class ColorDetection:
    def __init__(self, lower, upper, min_area = 50 * 50):
        self.set_color_range(lower, upper)
        self.min_area = min_area
        self.bbox = None

    def set_color_range(self, lower, upper):
        self.lower_color = np.array(lower)
        self.upper_color = np.array(upper)

    def set_min_area(self, area):
        self.min_area = area

    def detect(self, image, bbox = None):
        if bbox is None:
            bias = np.array([0, 0]).astype(np.int32)  # hand landmarks bias to left-top
        else:
            bias = bbox[0]  # hand landmarks bias to left-top
            # crop image
            image = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :]


        hsv_img = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        # Apply the inRange function to get the mask region
        mask = cv.inRange(hsv_img, self.lower_color, self.upper_color)
        # Find contours on mask
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # Initialize variables for largest blob
        largest_area = self.min_area
        largest_contour_index = -1
        # Loop through each contour and find the largest one
        for i in range(len(contours)):
            # Calculate area of contour
            area = cv.contourArea(contours[i])
            # Compare with previous largest area
            if area > largest_area:
                # Update largest area and contour index
                largest_area = area
                largest_contour_index = i
        # Get bounding box of the largest contour
        if largest_contour_index != -1:
            x, y, w, h = cv.boundingRect(contours[largest_contour_index])
            self.bbox = (np.array([[x, y], [x + w, y + h]]) + bias).astype(np.int32)
        else:
            self.bbox = None

        return self.bbox

    def visualize(self, image, label = "", thickness = 2):
        if self.bbox is not None:
            # Draw bounding box on original image (in color)
            cv.rectangle(image, self.bbox[0], self.bbox[1], (0, 255, 0), 2)
            cv.putText(image, '{}'.format(label), (self.bbox[0][0], self.bbox[0][1] + 22 * thickness), cv.FONT_HERSHEY_SIMPLEX, thickness, (0, 0, 255))
        return image
