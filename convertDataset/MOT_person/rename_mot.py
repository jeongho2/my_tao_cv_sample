""" mot_rename.py

MOTDet Dir - 여러 MOT Dir을 Train / Val 
묶음으로 학습시키기 위해 Dir 별로 중복된 이름을 고유한 이름을 가지도록 변경
"""
import os

mot_data_path = '/home/demo/Desktop/workspace/cv_samples_v1.3.0/myData/MOTDet'
dir_list = os.listdir(mot_data_path)

print(dir_list)

for dir in dir_list:
    if dir.startswith('MOT'):
        # image1 변환
        image_dir_path = mot_data_path + '/' + dir + '/' + 'img1'
        print(image_dir_path)
        image_file_list = os.listdir(image_dir_path) 
        
        for file in image_file_list :
            if not file.startswith('MOT'):
                old_name = image_dir_path + '/' + file
                # print(old_name)
                new_name = image_dir_path + '/' + dir + '_' + file
                print(new_name)

                try:
                    os.rename(old_name, new_name)
                    print("success : " + old_name + " -> " + new_name)
                except:
                    print("fail : " + old_name + " -> " + new_name)
                    break