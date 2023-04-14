# hsv_picker 工具说明

此工具用于获取 [`ColorDetection`](../../utils/ColorDetection.py) 检测颜色所使用的hsv色值范围，从而找到特定物体的位置信息。默认使用的是检测下图药瓶的色值范围

![](./bill%20bottle.png)

**使用方法：**

1. 将被检测物体的图片截图，只保留最关键的颜色信息
2. 修改 [`hsv_picker.py`](./hsv_picker.py) 文件中的 `source_img` 和 `target_img` 参数为图片路径
3. `target_img` 可以不和 `source_img`
   相同，只要最终显示的图片掩码里，目标颜色变成了白色，说明这个颜色可以被 `ColorDetection` 工具检测出来
4. 如果输出的hsv范围太大了，可以适当的调整，更改代码中的 21 和 22 行，将其中的 10, 50 改小一点
    ```python
    # line 21 and 22 
    lower_blue = np.array([h_mean - 10, s_mean - 50, v_mean - 50])
    upper_blue = np.array([h_mean + 10, s_mean + 50, v_mean + 50])
    ```
