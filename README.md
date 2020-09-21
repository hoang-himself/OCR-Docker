# OCR Demo
A docker repo for building some necessities for backend.

# IMPORTANT
- Go to your Firebase's project [service accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
- Click Generate New Private Key.
- Save as `serviceAccountKey.json` in `/back` folder.
### Not tested with duplicate files on Firebase.

# Known issues
- Cannot use fetch() with Docker's internal network, currently using lvh.me, because [fuck Google](https://bugs.chromium.org/p/chromium/issues/detail?id=67743)
- Firebase Storage takes quite long to refresh, and back-end fails to find the file. Maybe will implement front-end to save files to a Docker volume to process, then upload the file to Firebase.

# How to use
### Download this repository
### Install git-lfs
```
sudo apt install git-lfs
```
### Update submodules
```
cd OCR-Docker &&\
git submodule update --init
```

### Run with Docker Compose
```
docker-compose up --build -d
```
Server is available at `localhost:8000/`.\
All images are saved in Firebase Storage.

<br />

---

From [TokisakiKurumi2001](https://github.com/TokisakiKurumi2001) and [Smithienious](https://github.com/Smithienious).
