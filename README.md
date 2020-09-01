# Docker-backend
A docker repo for building some necessities for backend

# How to use
## Build Docker image
```bash
docker build -t [any_image_name_you_like] .
```
This will take very long on installing pytorch.

## Execute
```bash
docker run -it --name [any_container_name_you_like] -p 80:80 [image_name_you_just_made]
```
Go to `localhost:80/` to see result.

## Predict latitude, longitude
Hopefully it will work.
Navigate to `localhost:80/predict/pic_5.jpg?crs=9210`