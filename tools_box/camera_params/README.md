# camera_params 工具说明

<!-- TOC -->
* [camera_params 工具说明](#cameraparams-工具说明)
    * [相机标定使用说明](#相机标定使用说明)
    * [camera_capture 使用说明](#cameracapture-使用说明)
    * [camera_params 使用说明](#cameraparams-使用说明)
<!-- TOC -->

### 相机标定使用说明
1. 使用 `generate_chessboard.py` 生成棋盘图，并放在A4纸上打印。或者直接打印文件[`camera_chessboard.docx`](camera_chessboard.docx)，注意不要做任何缩放，打印出来的结果，每个棋盘格子大小应该为 `2.5cm*2.5cm`
2. 使用`camera_capture.py`获取15张棋盘图片，只要保证图片清晰、亮度均匀、角点可见、棋盘格不过于倾斜或弯曲即可。命名为: `board_0.jpg`, `board_1.jpg` ... `board_14.jpg`。将图片至于此目录下
3. 执行代码`camera_params.py`输出相机的内参和畸变系数

### camera_capture 使用说明
先更改代码文件中，需要使用的摄像头`cam`，可以是电脑摄像头，机器狗广角摄像头，机械臂摄像头。然后运行代码。按一次回车保存一次图片，超过15张后按q或Q退出程序

### camera_params 使用说明
直接运行代码后，会输出相机的内参矩阵和畸变系数，将其复制到 [robot_arm.py](../../robot_arm.py) 代码的对应位置替换原本的数值