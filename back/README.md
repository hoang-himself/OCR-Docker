# OCR Back-end
A docker repo for building some necessities for backend.

# IMPORTANT
- Go to your Firebase's project [service accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
- Click Generate New Private Key.
- Save as `serviceAccountKey.json` in the `/back` folder.
### Not tested with duplicate files on Firebase.

# Usage
### Update submodules
```
cd OCR-Docker &&\
git submodule update --init
```
Server is available at `localhost:8000/`.\
All images are downloaded from Firebase Storage.
