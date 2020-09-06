FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY /app /app
COPY serviceAccountKey.json /
COPY craft_mlt_25k.pth /app/CRAFT
COPY text_recognition.py /app/CRAFT
COPY text_to_coordinate.py /app/CRAFT

WORKDIR /app
RUN apt update &&\
    apt install -y tesseract-ocr g++ cmake libmagickwand-dev libgl1-mesa-glx &&\
    pip install --upgrade pip &&\
    pip install -r requirements.txt

WORKDIR /app/imgtxtenh
RUN cmake CMakeLists.txt &&\
    make

WORKDIR /
ENTRYPOINT ["sh","start.sh"]