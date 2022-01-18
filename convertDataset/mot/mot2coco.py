import os
import json
import cv2
import numpy as np
import configparser
import math

"""
   MOT : Frame_number Identity_number 


   COCO : bbox" : [x,y,width,height], 
"""
def convert2coco(dir_list):
    categories = [{'id': 0, 'name': 'person', "supercategory": "none"}]
    images = []
    annotations = []

    print(dir_list)
    img_id_offset = 0

    for dir_path in dir_list:
        print("dir_path : " + dir_path)
        s = dir_path.split('.')
        if len(s) > 1: continue
        f = open(os.path.join(dir_path, 'gt/gt.txt'), 'r')
        gt = []
        for line in f:
            info = [int(float(i)) for i in line[:-1].split(',')]
            # info = [print(int(float(i))) for i in line[:-1].split(',')]
            # info = [print(round(float(i))) for i in line[:-1].split(',')]
            # info = [int(round(float(i))) for i in line[:-1].split(',')]
            gt.append(info)
        f.close
        config = configparser.ConfigParser()
        config.read(os.path.join(dir_path, 'seqinfo.ini'))
        h = int(config['Sequence']['imHeight'])
        w = int(config['Sequence']['imWidth'])

        cls2cat = [1, 7]
        ann_id = 0
        img_list = np.unique(np.array(gt)[:,0])
        for im in img_list:
            # print(im)
            id = im + img_id_offset -1
            file_name = f'{im:06d}.jpg'
            # file_name = dir_path + file_name
            # file_name = os.path.join(dir_path, 'img1', file_name)
            # print("dir_path : " + dir_path + "file_name :" + file_name)
            file_name = dir_path + '_' + file_name
            images.append(
                {
                'id': int(id),
                'file_name': file_name,
                'height': h,
                'width': w}
            )


        for ann in gt:
            if ann[7] not in cls2cat and ann[-1] > 0.5: continue
            # print(ann[0])
            image_id = ann[0] + img_id_offset -1
            category_id = 0
            bbox = ann[2:6]
            # x, y, width, height
            if bbox[0] < 0:
                bbox[0] = 0

            if bbox[0] > w:
                bbox[0] = w
            
            if bbox[1] < 0:
                bbox[1] = 0
            
            if bbox[1] > h:
                bbox[1] = h

            if bbox[2] < 0:
                bbox[2] = 0
            
            if (bbox[0] + bbox[2]) > w:
                # print("x + width > w")
                # print("x : " + str(bbox[0]) + " width : " + str(bbox[2]) + "w :" + str(w))
                bbox[2] = w - bbox[0]
                # print("after width : " + str(bbox[2]))
            
            if bbox[3] < 0:
                bbox[3] = 0

            if (bbox[1] + bbox[3]) > h:
                # print("y + height > h")
                # print("y : " + str(bbox[1]) + " height : " + str(bbox[3]) + "h :" + str(h))
                bbox[3] = h - bbox[1]
                # print("after height : " + str(bbox[3]))


            # print('height :' + str(h) + ' width : ' + str(w))
            # print(bbox)
            annotations.append(
            {
                'id': ann_id,
                'image_id': image_id,
                'category_id': category_id,
                'bbox': bbox}
            )
            ann_id += 1
        
        img_id_offset += len(img_list)
        # print(img_id_offset)

    ann_dict = {
        'categories': categories,
        'images': images,
        'annotations': annotations
        }
    return ann_dict


train_dir = ['MOT17-02', 'MOT17-04', 'MOT17-13', 'MOT20-02', 'MOT17-10', 'MOT17-09', 'MOT20-05']
val_dir = ['MOT20-01', 'MOT20-03']
train_json = convert2coco(train_dir)
with open('train.json', 'w') as fp:
    json.dump(train_json, fp)

val_json = convert2coco(val_dir)
with open('val.json', 'w') as fp:
    json.dump(val_json, fp)

