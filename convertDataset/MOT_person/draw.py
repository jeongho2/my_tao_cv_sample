import os
import cv2
import numpy as np


dir_path = 'MOT17-04'
f = open(os.path.join(dir_path, 'gt/gt.txt'), )
gts = []
for line in f:
    info = [int(round(float(i))) for i in line[:-1].split(',')]
    gts.append(info)
person_cls = [1,7]
img_dir = os.path.join(dir_path, 'img1')
img_list = np.unique(np.array(gts)[:,0])
for im in img_list:
    file_name = f'{int(im):06d}.jpg'
    img = cv2.imread(os.path.join(dir_path, 'img1', file_name))
    # frame_gt = []
    # for gt in gts:
    #     if gt[0] == im:
    #         frame_gt.append(gt)
    # stop = 0
    for gt in gts:
        if gt[0] == im:
            if gt[7] in person_cls and gt[-1] > 0.5:
                bbox = np.array(gt[2:6])
                x1, y1 = bbox[0:2]
                x2, y2 = bbox[0:2] + bbox[2:4]
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255,0,0), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)