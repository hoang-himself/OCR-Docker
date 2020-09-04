from fastapi import FastAPI

import sys
import os
import subprocess
import ntpath

sys.path.append('/app/CRAFT/')
from text_recognition import text_recognition
from text_to_coordinate import text_to_coordinate

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate('serviceAccountKey.json')

default_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'fir-ocr-ec83a.appspot.com',
}, name='storage')

bucket = storage.bucket(app=default_app)

app = FastAPI()

os.chdir('/app/tmp')


@app.get('/')
def read_root():
    return {'Hello, World!'}


@app.get('/predict/{image}')
def read_image(image: str, crs: int):
    online_path = 'images/' + image
    offline_path = '/app/tmp/' + image
    blob = bucket.blob(online_path)
    with open(offline_path, 'wb') as file_obj:
        blob.download_to_file(file_obj)

    image = preprocess(offline_path)

    input_text = text_recognition(image)
    lon, lat = text_to_coordinate(input_text, crs)

    return 'https://www.google.com/maps/@?api=1&map_action=map&center=' + \
        str(lat) + ',' + str(lon) + '&zoom=15'


# * Correctly extract file name
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def preprocess(image_path: str):
    image_name = path_leaf(image_path)
    pre_image_name = 'pre_' + image_name + '.jpg'

    # * Using a dedicated folder for image processing, thus the working directory change
    command = '/app/imgtxtenh/imgtxtenh /app/tmp/' + \
        image_name + ' -p /app/tmp/' + pre_image_name
    process = subprocess.Popen(command, shell=True).wait()
    command = 'rm *.png'
    process = subprocess.Popen(command, shell=True).wait()

    return pre_image_name
