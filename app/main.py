from typing import Optional

from fastapi import FastAPI

import sys

sys.path.append("./app/CRAFT/")

from text_recognition import text_recognition
from text_to_coordinate import text_to_coordinate

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/predict/{image}")
def read_image(image: str, crs: int):
	input_text = text_recognition(image)
	lon, lat = text_to_coordinate(input_text)
	return {"latitude": lat, "longitude": lon}