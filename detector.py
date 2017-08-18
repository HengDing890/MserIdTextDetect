# -*- coding:utf-8 -*-
"""
detector.py
-------

文字定位器，
基于MSER算法，定位身份证中的文字区块.

@author: Heng Ding
@e-mail: hengding@whu.edu.cn
"""
import cv2, numpy as np

class TextDetector(object):
    """ 文字定位器类 """

    def __init__(self, img_path):
        self.img = cv2.imread(img_path)
        self.resize_img = self.transform()

    def transform(self):
        """ 归一化尺寸，将图片缩放到统一尺寸 """
        h, w, c = np.shape(self.img)
        f_h = 1920
        f_y = float(h) / 1920
        f_w = int(float(w) / f_y)
        resize_img = cv2.resize(self.img, (f_w, f_h), interpolation=cv2.INTER_AREA)
        return resize_img

    def hyp_parameters(self):
        """ 计算经验参数 """
        h, w, c = np.shape(self.resize_img)
        # 文字区块最小最大面积
        min_area, max_area = 27*27, 0.05 * h * w
        # 文字区块最小最大高度
        min_h, max_h = 50, 200
        return min_area, max_area, min_h, max_h

    def find_candidates(self):
        """ 返回候选文字区块坐标 """

        # 灰度化
        gray = cv2.cvtColor(self.resize_img, cv2.COLOR_BGR2GRAY)

        # 二值化
        _threshold = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

        # 腐蚀
        kernel = np.ones((27, 27), np.uint8)
        erosion = cv2.erode(_threshold, kernel, iterations = 2)

        # 轮廓检测
        _, contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 根据经验参数选取区域
        candidate_boxes = []
        min_area, max_area, min_h, max_h = self.hyp_parameters()

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if min_area < cv2.contourArea(cnt) < max_area and min_h < h < max_h:
                candidate_boxes.append((x,y,x+w,y+h))

        return candidate_boxes

    def split_candidates(self, box):
        """ 候选区块切割 """

        # 灰度化
        gray = cv2.cvtColor(self.resize_img, cv2.COLOR_BGR2GRAY)
        # 二值化
        _threshold = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

        # 腐蚀
        kernel = np.ones((3, 5), np.uint8)
        erosion = cv2.erode(_threshold, kernel, iterations = 2)

        # 获取区块对应腐蚀图像
        x1, y1, x2, y2 = box
        box_erosion = erosion[y1:y2, x1:x2]

        # 依据连续空白区域进行列切割
        his = np.mean(box_erosion, axis=0)
        split_indexes, flag = [0], True
        for i in range(len(his)):
            c = his[i]
            if c != 255 and flag is True:
                split_indexes.append(i)
                flag = False
            elif c == 255 and flag is False:
                split_indexes.append(i)
                flag = True
        split_indexes.append(len(his))

        assert len(split_indexes) % 2 == 0

        t = [int((i+j)/2) for i,j in zip(split_indexes[::2],split_indexes[1::2])]

        boxes = [(x1+t[i], y1, x1+t[i+1], y2) for i in range(len(t)-1) if t[i+1]-t[i]]

        return boxes

    def is_noisy(self, box):
        """ 基于坐标规则判断是否属于人脸噪声区块 """
        h, w, c = np.shape(self.resize_img)
        x1, y1, x2, y2 = box
        if (x1+x2)/2 > 0.65*w and (y1+y2)/2 < 0.7*h:
            return True
        return False

    def detect(self):
        # 初步查找候选区域
        candidate_boxes = self.find_candidates()

        # 初步候选区域切割
        split_boxes = []
        for candidate in candidate_boxes:
            if candidate[2]-candidate[0] > 100:
                split_boxes += self.split_candidates(candidate)
            else:
                split_boxes += [candidate]

        # 屏蔽人脸区域噪音
        final_boxes = []
        for box in split_boxes:
            if not self.is_noisy(box):
                final_boxes.append(box)

        return final_boxes


if __name__ == '__main__':
    d = TextDetector("./imgs/ID2.jpg")
    boxes = d.detect()
    for box in boxes:
        cv2.rectangle(d.resize_img, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 3)
    cv2.imwrite("./imgs/R2.jpg", d.resize_img)



