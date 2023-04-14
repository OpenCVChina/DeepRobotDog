# 导入所需的库
import cv2 as cv
import numpy as np

# 设置棋盘格的角点数
n_rows = 6
n_cols = 9

# 设置棋盘格的实际尺寸（单位：米）
square_size = 0.025

# 设置棋盘格的图片分辨率（单位：像素）
resolution = (900, 600)

# 创建一个空白的图片
img = np.zeros((resolution[1], resolution[0]), dtype=np.uint8)

# 设置棋盘格的颜色（黑白交替）
black = 0
white = 255

# 计算每个格子的大小（单位：像素）
cell_width = resolution[0] // n_cols
cell_height = resolution[1] // n_rows

# 绘制棋盘格
for i in range(n_rows):
    for j in range(n_cols):
        # 判断当前格子的颜色
        if (i + j) % 2 == 0:
            color = black
        else:
            color = white
        # 计算当前格子的左上角和右下角坐标
        x1 = j * cell_width
        y1 = i * cell_height
        x2 = (j + 1) * cell_width - 1
        y2 = (i + 1) * cell_height - 1
        # 填充当前格子的颜色
        img[y1:y2+1, x1:x2+1] = color

# 显示并保存图片
cv.imshow('img',img)
cv.waitKey(0)
cv.destroyAllWindows()
cv.imwrite('chessboard.jpg', img)