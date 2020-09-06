from typing import Optional
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import sys
import os
import subprocess
import ntpath

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

sys.path.append('/app/CRAFT/')
from text_recognition import text_recognition
from text_to_coordinate import text_to_coordinate


cred = credentials.Certificate('serviceAccountKey.json')

default_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'fir-ocr-ec83a.appspot.com',
}, name='storage')

bucket = storage.bucket(app=default_app)

app = FastAPI()

# * Fucking CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    lon = float(int(lon * 10000000) / 10000000)
    lat = float(int(lat * 10000000) / 10000000)

    # * Clean-up
    command = 'rm /app/tmp/*'
    process = subprocess.Popen(command, shell=True).wait()

    return {'lon': lon, 'lat': lat}


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
