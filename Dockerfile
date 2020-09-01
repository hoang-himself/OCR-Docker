FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
COPY ./app /app
RUN pip install --upgrade pip
RUN pip install -r requirement.txt
RUN apt update
RUN apt-get -y install tesseract-ocr
RUN apt-get -y install make
RUN apt-get -y install gcc
RUN apt-get -y install g++
RUN apt-get -y install cmake
RUN apt-get -y install libmagickcore-6.q16-dev
RUN apt-get -y install libgl1-mesa-dev
WORKDIR ./imgtxtenh
RUN cmake CMakeLists.txt -DCMAKE_BUILD_TYPE=Release
RUN make
RUN export PATH="$PATH:`pwd`"
WORKDIR /
COPY pic_5.jpg pic_5.jpg
ENTRYPOINT ["sh","start.sh"]