import sys
from fastapi import FastAPI
from typing import Optional

sys.path.append("./app/CRAFT/")
from text_to_coordinate import text_to_coordinate
from text_recognition import text_recognition


app = FastAPI()


@app.get("/")
def read_root():
    return "Hello, World!"


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/predict/{image}")
def read_image(image: str, crs: int):
    input_text = text_recognition(image)
    lon, lat = text_to_coordinate(input_text, crs)
    return 'https://www.google.com/maps/@?api=1&map_action=map&center=' + \
        str(lat) + ',' + str(lon) + '&zoom=15'
