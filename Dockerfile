FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY /app /app

WORKDIR /app
RUN apt update &&\
    apt install -y tesseract-ocr g++ cmake libmagickwand-dev libgl1-mesa-glx &&\
    pip install --upgrade pip &&\
    pip install -r requirement.txt

WORKDIR /app/imgtxtenh
RUN cmake CMakeLists.txt -DCMAKE_BUILD_TYPE=Release &&\
    make

WORKDIR /
COPY pic_5.jpg pic_5.jpg
ENTRYPOINT ["sh","start.sh"]