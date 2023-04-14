# grid_image 工具介绍
此工具用来确定路标的标定点位置，用于判断不同的标志。

**使用方法：**
1. 修改 [`grid.py`](./grid.py) 文件中的img读取的图片文件
2. 执行代码
3. 获得一张类似如下输出的图片
    ![](../../doc_static/grid_image_demo.png)
4. 数出用于标定的像素格的x和y的位置
5. 如果想更细粒度，则可以将50改成其他数值，但是相应的 [`DangerSignRecognition.py`](../../utils/DangerSignRecognition.py) 和 [`RoadSignRecognition`](../../utils/RoadSignRecognition.py) 中设置的缩放系数改成新数值