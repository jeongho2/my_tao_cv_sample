import json

annotation_object_json = "/home/jeongho/Desktop/workspace/cv_samples_v1.3.0/myData/raw-data/annotations/train.json"
annotation_caption_json = "/home/jeongho/Desktop/workspace/cv_samples_v1.3.0/myData/raw-data/annotations/caption.json"

size_of_lenght = 0

with open(annotation_object_json, "r") as json_file:
    json_data = json.load(json_file)
    size_of_lenght = len(json_data["images"])

dump_data = {}
anno = []
images = []

for i in range(size_of_lenght):
    tmp1={}
    tmp1["image_id"] = i
    tmp1["id"] = i
    tmp1["caption"] = ""
    anno.append(tmp1)

    tmp2={}
    tmp2["id"] = i
    images.append(tmp2)

dump_data["annotations"] = anno
dump_data["images"] = images

with open(annotation_caption_json, 'w') as outfile:
    json.dump(dump_data, outfile, indent=4)

print('finish')