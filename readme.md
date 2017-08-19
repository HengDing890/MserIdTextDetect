# 说明 #

第二代身份证文字区块切割与提取

* 本程序仅支持90%以上区域为身份证信息的图像识别

## 使用方法 ##

请先安装依赖包opencv和numpy

``` python
import cv2
from detector import TextDetector

# 读取身份证图片
img = cv2.imread("./imgs/")

# 新建文字检测器，提取文字区块
d = TextDetector("./imgs/ID2.jpg")
boxes = d.detect()

# 在图片上画出文字区块
for box in boxes:
    cv2.rectangle(d.resize_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 3)

# 输出检测后图片
cv2.imwrite("./imgs/R2.jpg", d.resize_img)
```
