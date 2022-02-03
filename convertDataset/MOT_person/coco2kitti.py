""" coco2kitti.py: Convert MS COCO annotation files to 
            bounding box label files in Kitti format 
            to provide Kitti data format in training 
            with TAO toolkit.

참고 :https://docs.nvidia.com/tao/tao-toolkit/text/data_annotation_format.html#object-detection-kitti-format

# TAO Kitti Format
class_names truncation occlustion alpha bounding_box(xmin ymin xmax ymax) 3D_dimension(Height width lenght) Location, Rotation_y 

# TAO COCO Format
"categories" : [{id, name, supercategory}],
"images" : [{id, license, file_name, height, width, date_captured}],
"annotations" : [{id, image_id, category_id, bbox:[], area, segmetation, iscrowd()}]

__author__ = "Jeongho Kim"
"""

import os
from pycocotools.coco import COCO

def coco2kitti(catNms, annFile):
    # initialize COCO api for instance annotations
    print(annFile)
    coco = COCO(annFile)
    # Create an index for the category names
    cats = coco.loadCats(coco.getCatIds())
    print(cats)
    cat_idx = {}
    for c in cats:
        cat_idx[c['id']] = c['name']
    myCnt = 0
    for img in coco.imgs:
        # print(myCnt)
        myCnt = myCnt+1
        # print(img)
        # Get all annotation IDs for the image
        catIds = coco.getCatIds(catNms=catNms)
        annIds = coco.getAnnIds(imgIds=[img], catIds=catIds)

        # If there are annotations, create a label file
        # print(len(annIds))
        if len(annIds) > 0:
            # Get image filename
            img_fname = coco.imgs[img]['file_name']
            # print(img_fname)
            # open text file
            with open('./labels/' + os.path.splitext(img_fname)[0] + '.txt','w') as label_file:
                anns = coco.loadAnns(annIds)
                for a in anns:
                    bbox = a['bbox']
                    # Convert COCO bbox coords to Kitti ones
                    bbox = [bbox[0], bbox[1], bbox[2] + bbox[0], bbox[3] + bbox[1]]
                    bbox = [str(b) for b in bbox]
                    catname = cat_idx[a['category_id']]
                    # Format line in label file
                    # Note: all whitespace will be removed from class names
                    out_str = [catname.replace(" ","")
                               + ' ' + ' '.join(['0']*3)
                               + ' ' + ' '.join([b for b in bbox])
                               + ' ' + ' '.join(['0']*7)
                               +'\n']
                    label_file.write(out_str[0])

if __name__ == '__main__':

    # These settings assume this script is in data directory
    # dataType = 'train'
    dataType = 'val'

    # annFile = '%s/annotations/%s.json' % (dataDir, dataType)
    annFile = 'annotations/%s.json' % (dataType)

    # If this list is populated then label files will only be produced
    # for images containing the listed classes and only the listed classes
    # will be in the label file
    # EXAMPLE:
    #catNms = ['person', 'dog', 'skateboard']
    # catNms = ['raccoon']
    catNms = ['person']

    # Check if a labels file exists and, if not, make one
    # If it exists already, exit to avoid overwriting
    if os.path.isdir('./labels'):
        print('Labels folder already exists - exiting to prevent badness')
    else:
        os.mkdir('./labels')
        coco2kitti(catNms, annFile)