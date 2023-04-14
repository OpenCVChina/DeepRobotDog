import numpy as np
import cv2 as cv

if __name__ == '__main__':
    # 设置棋盘格的角点数
    n_rows = 5
    n_cols = 8

    # 设置棋盘格的实际尺寸（单位：米）
    square_size = 0.025

    # 创建棋盘格的三维坐标点
    objp = np.zeros((n_rows * n_cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:n_rows, 0:n_cols].T.reshape(-1, 2) * square_size

    # 创建存储三维点和图像点的列表
    objpoints = []  # 三维点
    imgpoints = []  # 图像点

    # 读取所有的棋盘格图片
    images = []
    for i in range(0, 15):
        images.append('board_{}.jpg'.format(i))

    # 遍历每张图片，寻找角点
    gray = None
    for path in images:
        # 读取图片并转为灰度图
        img = cv.imread(path)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # 寻找角点
        ret, corners = cv.findChessboardCorners(gray, (n_rows, n_cols), None)

        # 如果找到了，添加到三维点和图像点列表中
        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)

            # 绘制并显示角点
            cv.drawChessboardCorners(img, (n_rows, n_cols), corners, ret)
            # cv.imshow('img', img)
            # cv.waitKey(500)

    cv.destroyAllWindows()
    if gray is not None:
        # 标定相机，获取内参矩阵和畸变系数
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        h, w = gray.shape[:2]
        newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

        # 打印结果
        np.set_printoptions(suppress=True)
        print("内参矩阵：")
        print(np.array2string(np.round(newcameramtx, 4), separator=','))
        print("畸变系数：")
        print(np.array2string(np.round(dist[0], 4), separator=','))
