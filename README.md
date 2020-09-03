# Docker-backend
A docker repo for building some necessities for backend.

# How to use
## Run with Docker Compose
```
docker-compose up
```
This will take very long on installing torch.

Go to `localhost:5000/` to see result.

## Extract latitude, longitude
Navigate to `localhost:5000/predict/pic_1.jpg?crs=9210` for example.
All images are saved in root for the mean time.
Also available at `https://obscure-retreat-69161.herokuapp.com:8080` but there is a problem with memory quota.

# How to get serviceAccountKey
- Go to your Firebase's project [service accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
- Click Generate New Private Key.
- The key credentials are saved in ```serviceAccountKey.json``` in the root folder.