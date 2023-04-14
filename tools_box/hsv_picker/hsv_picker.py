import cv2 as cv
import numpy as np

# Read source image
source_img = cv.imread("bill bottle.png")
# Read target image
target_img = cv.imread("bill bottle.png")

# Convert to HSV colorspace
source_hsv = cv.cvtColor(source_img, cv.COLOR_BGR2HSV)

# Convert target image to HSV colorspace
target_hsv = cv.cvtColor(target_img, cv.COLOR_BGR2HSV)

# Get average values of each channel
h_mean = np.mean(target_hsv[:, :, 0])
s_mean = np.mean(target_hsv[:, :, 1])
v_mean = np.mean(target_hsv[:, :, 2])

# Define lower and upper bounds for color
lower_blue = np.array([h_mean - 10, s_mean - 50, v_mean - 50])
upper_blue = np.array([h_mean + 10, s_mean + 50, v_mean + 50])
lower_blue = np.maximum(lower_blue, 0)
upper_blue = np.maximum(upper_blue, 0)
lower_blue = np.minimum(lower_blue, [179, 255, 255])
upper_blue = np.minimum(upper_blue, [179, 255, 255])
print("When the 'Mask' shows almost 'white' pixels, it means that the color can be detected.")
print("Lower Color: {}, Upper Color: {}".format(lower_blue, upper_blue))

# Apply inRange() function
mask = cv.inRange(source_hsv, lower_blue, upper_blue)

# Find contours on mask image
contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# Draw bounding rectangles for each contour
for cnt in contours:
    x, y, w, h = cv.boundingRect(cnt)
    cv.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), 1)

# Display mask image
cv.imshow("Mask", mask)
cv.waitKey(0)
cv.destroyAllWindows()
