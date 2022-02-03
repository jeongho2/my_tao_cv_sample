import os

lpr_data_path = '/home/jeongho/Desktop/workspace/cv_samples_v1.3.0/myData/lprDataset/clean_data'
dir_list = os.listdir(lpr_data_path)

print(dir_list)

cnt = 0

for dir in dir_list:
    label_dir_path = lpr_data_path + '/' + dir + '/' + 'label'
    print(label_dir_path)
    label_file_list = os.listdir(label_dir_path) 
    
    for label_file_name in label_file_list :
        label_file_path = label_dir_path + '/' + label_file_name

        file_name = os.path.splitext(label_file_name)[0]

        label_file = open(label_file_path, "r")
        label = label_file.read()
        label_file.close()

        isDirty = False

        if 'x' in label:
            isDirty = True
            print('in x :')
            print(label_file_path)
        if 'X' in label:
            isDirty = True
            print('in X :')
            print(label_file_path)
        if ' ' in label:
            isDirty = True
            print('in  : ')
            print(label_file_path)

        if isDirty :
            cnt = cnt + 1
            image_file_path = label_dir_path + '/../image/' + file_name + '.jpg'
            # print('isDirty : ' + image_file_path)
            try:
                os.remove(label_file_path)
                print("success : " + label_file_path + " remove ")
            except:
                print("fail : " + label_file_path + " remove ")
                break
            
            try:
                os.remove(image_file_path)
                print("success : " + image_file_path + " remove ")
            except:
                print("fail : " + image_file_path + " remove ")
                break


print ('end cleaning ... count : ' + str(cnt))