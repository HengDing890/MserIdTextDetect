# 说明 #

第二代身份证文字区块切割与提取

## 使用方法 ##

请先按照依赖包opencv和numpy

``` python
import cv2
from detector import Detector

# 读取身份证图片
img = cv2.imread("./imgs/")

# 新建文字检测器，提取文字区块
text_detector = Detector(img)
text_boxes = detector.bounding()

# 在图片上画出文字区块，并编号
num = 1
for box in boxes:
    cv2.rectangle(detector.resize_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 3)
    cv2.putText(detector.resize_img, str(num), (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 3.0, (0, 0, 255), 3, 0)
    num += 1

# 输出检测后图片
cv2.imwrite("./imgs/Result.jpg", detector.resize_img)
```
