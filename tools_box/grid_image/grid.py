# 使用其他的方法来划分网格的代码
import cv2

# 读取图像
img = cv2.imread('./injured.png')

# 获取图像的高度和宽度
height, width = img.shape[:2]

# 定义一个n*n的网格，这里假设n为4
n = 50

# 定义一个列表，用于存储每个网格的左上角和右下角坐标
grids = []

# 遍历每个网格
for i in range(n):
    for j in range(n):
        # 计算当前网格的左上角和右下角坐标，使用round函数来四舍五入
        x1 = round(j * width / n)
        y1 = round(i * height / n)
        x2 = round((j + 1) * width / n)
        y2 = round((i + 1) * height / n)

        # 将当前网格的坐标添加到列表中
        grids.append((x1, y1, x2, y2))

# 遍历每个网格
for (x1, y1, x2, y2) in grids:
    # 绘制当前网格的边框，颜色为红色，线宽为2
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 1)

# 显示结果图像
cv2.imshow('Result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()