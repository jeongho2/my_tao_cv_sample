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
def convert2coco(dir_list, val=False):
    categories = [{'id': 0, 'name': 'person', "supercategory": "none"}]
    images = []
    annotations = []
    img_id_offset = 0
    ann_id = 0 
    for dir_path in dir_list:
        print("dir_path : " + dir_path)
        s = dir_path.split('.')
        if len(s) > 1: continue
        f = open(os.path.join(dir_path, 'gt/gt.txt'), 'r')
        gt = []
        for line in f:
            # info = [int(float(i)) for i in line[:-1].split(',')]
            info = [int(round(float(i))) for i in line[:-1].split(',')]
            gt.append(info)
        f.close
        config = configparser.ConfigParser()
        config.read(os.path.join(dir_path, 'seqinfo.ini'))
        h = int(config['Sequence']['imHeight'])
        w = int(config['Sequence']['imWidth'])

        cls2cat = [1, 7]
        img_list = np.unique(np.array(gt)[:,0]).tolist()
        img_id = 0

        if val:
            img_list = np.random.choice(img_list, int(len(img_list)/10)).tolist()
        for im in img_list:
            id = img_id + img_id_offset
            file_name = f'{im:06d}.jpg'
            # file_name = dir_path + file_name
            # file_name = os.path.join(dir_path, 'img1', file_name)
            file_name = dir_path + '_' + file_name
            images.append(
                {
                    'id': int(id),
                    'file_name': file_name,
                    'height': h,
                    'width': w
                }
            )
            img_id += 1

        for ann in gt:
            print('annn')
            # x, y, width, height
            bbox = ann[2:6]

            # boundary check
            if bbox[0] < 0: bbox[0] = 0
            if bbox[0] > w: bbox[0] = w
            
            if bbox[1] < 0: bbox[1] = 0
            if bbox[1] > h: bbox[1] = h

            if bbox[2] < 0: bbox[2] = 0
            if (bbox[0] + bbox[2]) > w: bbox[2] = w - bbox[0]
            
            if bbox[3] < 0: bbox[3] = 0
            if (bbox[1] + bbox[3]) > h: bbox[3] = h - bbox[1]

            if ann[7] not in cls2cat or ann[-1] < 0.5: 
                print('not cls2cat')
                continue #
            if bbox[3]/bbox[2] < 0.5 or bbox[3]/bbox[2] > 6: 
                print('not 0.5 6')
                continue # 6 가로 세로 비율

            if ann[0] in img_list:
                image_id = img_list.index(ann[0]) + img_id_offset
                category_id = 0                
                w = images[image_id]['width']
                h = images[image_id]['height']
                annotations.append(
                    {
                        'id': ann_id,
                        'image_id': image_id,
                        'category_id': category_id,
                        'bbox': bbox,
                        'area': bbox[2] * bbox[3],
                        'iscrowd': 0
                    }
                )
                ann_id += 1
        img_id_offset += img_id

    ann_dict = {
        'categories': categories,
        'images': images,
        'annotations': annotations
        }
    return ann_dict


train_dir = ['MOT17-02', 'MOT17-04', 'MOT17-09', 'MOT17-10', 'MOT17-13', 'MOT20-02', 'MOT20-05']
val_dir = ['MOT20-01', 'MOT20-03']
train_json = convert2coco(train_dir)
with open('train.json', 'w') as fp:
    json.dump(train_json, fp)

val_json = convert2coco(val_dir, val=False)
with open('val.json', 'w') as fp:
    json.dump(val_json, fp)

