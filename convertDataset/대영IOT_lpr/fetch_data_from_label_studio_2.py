import argparse
import cv2
import json
import numpy as np
from os.path import basename, splitext
from PIL import Image
from prettytable import PrettyTable
import requests
import sys
from tqdm import tqdm
from urllib import parse

def input_among_projects(projects):
    table = PrettyTable()
    table.field_names = ['id', 'title', 'created_at', 'task_number', 'total_annotations_number', 'total_predictions_number']
    for project in projects['results']:
        row = []
        for field in table.field_names:
            if project[field]:
                row.append(project[field])
            else:
                row.append(None)
        table.add_row(row)
    print(table)
    return input('[?] Enter Project id > ')

def input_to_fetch_exported_data(data):
    # print(data)
    return input('[?] Fetch all data > ')

def solving_vertex(pts):
    points = np.zeros((4,2), dtype= "uint32") #x,y쌍이 4개 쌍이기 때문
    #원점 (0,0)은 맨 왼쪽 상단에 있으므로, x+y의 값이 제일 작으면 좌상의 꼭짓점 / x+y의 값이 제일 크면 우하의 꼭짓점
    s = pts.sum(axis = 1)
    points[0] = pts[np.argmin(s)] #좌상
    points[3] = pts[np.argmax(s)] #우하
    #원점 (0,0)은 맨 왼쪽 상단에 있으므로, y-x의 값이 가장 작으면 우상의 꼭짓점 / y-x의 값이 가장 크면 좌하의 꼭짓점
    diff = np.diff(pts, axis = 1)
    points[2] = pts[np.argmin(diff)] #우상
    points[1] = pts[np.argmax(diff)] #좌하
    return points

def transformation(img, pts):
    src_np = np.array(pts, dtype=np.float32)

    mn, mx = np.amin(pts, axis=0), np.amax(pts, axis=0)
    dst_np = np.array([
    [mn[0], mn[1]],
    [mn[0], mx[1]],
    [mx[0], mn[1]],
    [mx[0], mx[1]]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(src=src_np, dst=dst_np)

    result = cv2.warpPerspective(img, M, dsize=(0,0))
    return result


def crop_images(exported):
    for data in exported:
        if not data['annotations'][0]['result']:
            continue
        for result in data['annotations'][0]['result']:
            if 'text' not in result['value']:
                continue

            # loc = 'val' if data['id'] > 200 else 'train'
            # loc = 'train'
            loc = 'val'

            with open(loc + '/label/' + splitext(basename(data['data']['local_image']))[0] + '.txt', 'w') as file:
                for txt in result['value']['text']:
                    file.write(txt)
            img = cv2.imread(data['data']['local_image'])
            # img[y: y + h, x: x + w]   
            
            x = int(round(result['value']['x'] * result['original_width']/100))
            y = int(round(result['value']['y'] * result['original_height']/100))
            w = int(round(result['value']['width'] * result['original_width']/100))
            h = int(round(result['value']['height'] * result['original_height']/100))

            print(data['data']['local_image'])

            if result['original_width'] == 1:
                # print(img)
                continue
            cv2.imwrite(loc + '/image/' + basename(data['data']['local_image']), img[y: y + h, x : x + w, :])

        
# url=http://106.252.251.68:8080
# auth='Authorization: Token 479b15979b6f8de2443dc302c35a541516cb1500'
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data Fetch from the Label Studio')
    parser.add_argument("--url", type=str, required=True, help="The url of the Label Studio")
    parser.add_argument("--auth", type=str, required=True, help="The Authentication Token of the Label Studio")
    parsed = parser.parse_args(sys.argv[1:])

    # 503 에러 임시 해결
    cookie = '_ga=GA1.1.1698911528.1643090613; _gid=GA1.1.263791940.1643090613; csrftoken=HMyzwysRcCiINd8H5ye8VUGCLgO9TUi3pUr0eZdr5p89CaQp2sptOxZnJPwEjRtj; sessionid=.eJxVjjsOgzAQRO-yNSAM_lKmzxnQem0DIbIjPk2i3D0moqGcmTej-cA-OegAkbgVAktNWpQ8SFta5ZvSEGliKvhaKCggLQPG6Y3blGL_mqFjBfS4b2O_r37p_1OMwcW0SLOPR-IeGIdUUYrbMtnqQKozXat7cv55O9nLwIjrmNvGtE56Q9rVDSOS-ZFXUnHZ1Do02dUknbToVNZcMlLGhIyioqCxRfj-AG6OSyI:1nCYHZ:Q9iiFj8gFDgWZWp-EN1szNXKwPPl7n_PSx2zbaAA6as'
   
    # Listup projects in the Label Studio
    response = requests.get('{}/api/projects/'.format(parsed.url),
                            headers={'Authorization': '{}'.format(parsed.auth)})
    if response.status_code != 200:
        raise RuntimeError('disallow the response to list up projects in the label studio={}'.format(response))
    
    projects = json.loads(response.text)
    print(projects['count'])
    print(projects['results'][0])
    if projects['count'] < 1:
        raise RuntimeError('zero count of projects={}'.format(projects['count']))
    pid = input_among_projects(projects)
    # Export tasks and annotations
    response = requests.get('{}/api/projects/{}/export?/exportType=JSON'.format(parsed.url, pid),
                            headers={'Authorization': '{}'.format(parsed.auth)})
    if response.status_code != 200:
        raise RuntimeError('disallow the response to export tasks and annotations in the label studio={}'.format(response))

    exported = json.loads(response.text)
    # print(exported)
    if not len(exported):
        raise RuntimeError('zero count of projects={}'.format(projects['count']))
    fetch = input_to_fetch_exported_data(exported)
    if fetch == '1':
        for data in tqdm(exported):
            data['data']['local_image'] = './data/' + basename(data['data']['ocr'])
            response = requests.get('{}{}'.format(parsed.url, data['data']['ocr']),
                                    headers={
                                        'Authorization': '{}'.format(parsed.auth),
                                        'Cookie': '{}'.format(cookie)
                                    })
            print(response)

            with open(data['data']['local_image'], 'wb') as file:
                file.write(response.content)
            
    crop_images(exported)