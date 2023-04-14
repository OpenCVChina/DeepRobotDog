import cv2 as cv

cam = cv.VideoCapture(0) # 默认电脑摄像头
# cam = cv.VideoCapture("/dev/video0", cv.CAP_V4L2) # 机器狗广角摄像头
# cam = cv.VideoCapture("/dev/video4", cv.CAP_V4L2) # 机械臂摄像头

img_counter = 0
while True:
    ret, frame = cam.read()
    k = cv.waitKey(1)
    if k == 113 or k == 81:  # q or Q to quit
        break
    if not ret:
        continue
    cv.imshow("test", frame)

    # 如果按下回车键，保存图片
    if k == 13:
        img_name = "board_{}.jpg".format(img_counter)
        cv.imwrite(img_name, frame)
        print("{} 已保存".format(img_name))
        img_counter += 1

cam.release()
cv.destroyAllWindows()