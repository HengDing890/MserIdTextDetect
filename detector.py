# -*- coding:utf-8 -*-
"""
detector.py
-------

文字定位器，
基于MSER算法，定位身份证中的文字区块.

@author: Heng Ding
@e-mail: hengding@whu.edu.cn
"""
import cv2
import numpy as np


class Detector(object):
    """文字定位器类.

    Attributes:
        input_img: 原始输入图片(cv2 format).
        resize_img: 尺寸变化后的图片.

    """

    def __init__(self, cv2_img):
        """

        :param cv2_img:
        """
        self.input_img = cv2_img
        self.resize_img = self.transform()
        # self.resize_img = self.input_img

    def transform(self):
        """归一化尺寸"""
        h, w, c = np.shape(self.input_img)
        f_h = 1920
        f_y = float(h) / 1920
        f_w = int(float(w) / f_y)
        resize_img = cv2.resize(self.input_img, (f_w, f_h), interpolation=cv2.INTER_AREA)
        return resize_img

    def bounding(self):
        """返回文字区块坐标"""

        def tune_regions(roi_image, x, y):
            """调整文字外框大小"""
            blur = cv2.GaussianBlur(roi_image, (5, 5), 0)
            _threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            if len(_threshold.shape) == 3:
                flatImage = np.max(_threshold, 2)
            else:
                flatImage = _threshold
            assert len(flatImage.shape) == 2
            rows = np.where(np.min(flatImage, 0) == 0)[0]
            x_start, x_end = np.min(rows), np.max(rows)
            cols = np.where(np.min(flatImage, 1) == 0)[0]
            y_start, y_end = np.min(cols), np.max(cols)
            return x + x_start, y + y_start, x + x_end, y + y_end

        def merge_boxes(sorted_line_boxes):
            """如果一行中相邻的两个区块有重叠，则将其合并"""
            no_overlap_boxes = []
            i = 0
            while i < len(sorted_line_boxes)-1:
                cur_box = sorted_line_boxes[i]
                next_box = sorted_line_boxes[i+1]
                if cur_box[2] <= next_box[0]:
                    no_overlap_boxes.append(cur_box)
                    i += 1
                else:
                    x1 = min([cur_box[0], cur_box[2], next_box[0], next_box[2]])
                    x2 = max([cur_box[0], cur_box[2], next_box[0], next_box[2]])
                    no_overlap_boxes.append((x1, cur_box[1], x2, cur_box[3]))
                    i = i+2
            if i+1 == len(sorted_line_boxes):
                no_overlap_boxes.append(sorted_line_boxes[i])
            return no_overlap_boxes

        gray = cv2.cvtColor(self.resize_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 3)

        # MSER检测
        mser = cv2.MSER_create()
        regions = mser.detectRegions(blur, None)
        contours = [p.reshape(-1, 1, 2) for p in regions]

        # mask图像
        mask = gray.copy()
        mask[:] = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            mask[y:y + h, x:x + w] = 255
        _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 初步boxes
        init_boxes, ws, hs = [], [], []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            x1, y1, x2, y2 = tune_regions(gray[y:y + h, x:x + w], x, y)
            init_boxes.append((x1, y1, x2, y2))
            ws.append(x2-x1)
            hs.append(y2-y1)

        # 平均字体大小
        mean_w, mean_h = np.mean(ws), np.mean(hs)
        tmp_boxes, range_mask = [], np.zeros(1920)
        for x1, y1, x2, y2 in init_boxes:
            if x2-x1 >= mean_w/3.0 and y2-y1 >= mean_h/3.0:
                tmp_boxes.append((x1, y1, x2, y2))
                for i in range(y1, y2):
                    range_mask[i-1] = 1

        # 文字区块处理与排序
        tmp, flag = [], False
        for i in range(1920):
            if range_mask[i] != flag:
                tmp.append(i)
                flag = not flag

        final_boxes = []
        for i in range(0, len(tmp), 2):
            line_boxes = []
            h_start, h_end = tmp[i], tmp[i+1]
            for x1, y1, x2, y2 in tmp_boxes:
                if y1 > h_start-5 and y2 < h_end+5:
                    line_boxes.append((x1, h_start, x2, h_end))
            sorted_line_boxes = sorted(line_boxes, key=lambda t: t[0])
            final_boxes += merge_boxes(sorted_line_boxes)

        return final_boxes

if __name__ == "__main__":
    img = cv2.imread("./imgs/ID.jpg")
    detector = Detector(img)
    boxes = detector.bounding()

    num = 1
    for box in boxes:
        cv2.rectangle(detector.resize_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 3)
        cv2.putText(detector.resize_img, str(num), (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 3.0, (0, 0, 255), 3, 0)
        num += 1

    cv2.imwrite("./imgs/Result.jpg", detector.resize_img)
