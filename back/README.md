# OCR Back-end
A docker repo for building some necessities for backend.

# IMPORTANT
- Go to your Firebase's project [service accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
- Click Generate New Private Key.
- Save as `serviceAccountKey.json` in the `/back` folder.
### Not tested with duplicate files on Firebase.

# Usage
```
localhost:5000/
```
```
localhost:5000/predict/<image>?crs=<crs>
```
All images are downloaded from Firebase Storage.
