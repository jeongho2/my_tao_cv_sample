test2 = {}
test2["annotations"] = {}
test2["images"] = {}
tmp_anno = []
tmp_images = []
for i in range(30):
    tmp1={}
    tmp1["image_id"] = i
    tmp1["id"] = i
    tmp1["caption"] = ""
    tmp_anno.append(tmp1)

    tmp2={}
    tmp2["id"] = i
    tmp_images.append(tmp2)

test2["annotations"] = tmp_anno
test2["images"] = tmp_images

print(test2)