# Docker-backend
A docker repo for building some necessities for backend.

# IMPORTANT
- Go to your Firebase's project [service accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
- Click Generate New Private Key.
- Save as `serviceAccountKey.json` in the root folder.
### Not tested with duplicate files on Firebase.

# How to use
## Run with Docker Compose
```
docker-compose build && docker-compose up -d
```
Server is available at `localhost:5000/`.

## Extract latitude, longitude
```localhost:5000/predict/<image>?crs=<crs>```
All images are taken directly from Firebase Storage.
