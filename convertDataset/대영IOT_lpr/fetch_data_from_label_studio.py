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
            if 'points' not in result['value'] or 'text' not in result['value']:
                continue
            loc = 'val' if data['id'] > 200 else 'train'
            with open(loc + '/label/' + splitext(basename(data['data']['local_image']))[0] + '.txt', 'w') as file:
                for txt in result['value']['text']:
                    file.write(txt)
            img = cv2.imread(data['data']['local_image'])
            arr = np.array(result['value']['points'], dtype=np.int64)
            arr = np.int64(arr * [result['original_width']/100, result['original_height']/100])

            # rotate image
            vertex = solving_vertex(arr)
            # 0 : 좌상 1 : 좌하 2 : 우상 3 : 우하
            rotate_img = transformation(img, vertex)

            mn, mx = np.amin(arr, axis=0), np.amax(arr, axis=0)
            cv2.imwrite(loc + '/image/' + basename(data['data']['local_image']), img[mn[1]:mx[1], mn[0]:mx[0], :])

            # img[y: y + h, x: x + w]
            # cv2.imwrite(loc + '/image/' + basename(data['data']['local_image']), img[mn[1]:mx[1], mn[0]:mx[0], :])
            # cv2.imwrite(loc + '/image/rotate_' + basename(data['data']['local_image']), rotate_img[vertex[0][1]:mx[1], vertex[0][0]:mx[0], :])

            # cv2.imwrite(loc + '/image/' + basename(data['data']['local_image']), img[vertex[0][1]:mx[1], vertex[0][0]:mx[0], :])

# url=http://192.168.1.49:8080
# auth='Authorization: Token 85953519d5275a9077855e302c8283a5f05cabe8'
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data Fetch from the Label Studio')
    parser.add_argument("--url", type=str, required=True, help="The url of the Label Studio")
    parser.add_argument("--auth", type=str, required=True, help="The Authentication Token of the Label Studio")
    parsed = parser.parse_args(sys.argv[1:])

    # Listup projects in the Label Studio
    response = requests.get('{}/api/projects/'.format(parsed.url),
                            headers={'Authorization': '{}'.format(parsed.auth)})
    if response.status_code != 200:
        raise RuntimeError('disallow the response to list up projects in the label studio={}'.format(response))
    
    projects = json.loads(response.text)
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
    # print(fetch)
    if fetch == '1':
        print('fetch == 1')
        for data in tqdm(exported):
            data['data']['local_image'] = './data2/' + basename(data['data']['image'])
            response = requests.get('{}{}'.format(parsed.url, data['data']['image']),
                                    headers={'Authorization': '{}'.format(parsed.auth)})
            print(response)
            print(response.headers)
            print(parsed.url)
            print('{}{}'.format(parsed.url, data['data']['image']))

            with open(data['data']['local_image'], 'wb') as file:
                file.write(response.content)
            
    crop_images(exported)