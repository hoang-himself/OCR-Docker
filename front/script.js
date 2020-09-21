function uuid() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function successfullyGet(filename) {
  const crs = document.querySelector("#crs").value;

  // https://stackoverflow.com/questions/43871637/no-access-control-allow-origin-header-is-present-on-the-requested-resource-whe
  // const proxyurl = "https://cors-anywhere.herokuapp.com/";
  // var link = "https://ocrbackend.azurewebsites.net/predict/";
  var link = "http://lvh.me:8000/predict/";
  link += `${crs}-${filename}`;
  link += "?crs=";
  link += crs;
  fetch(link)
    .then((response) => response.json())
    .then((data) => {
      if (data["lon"] == -1 && data["lat"] == -1) {
        // Picture is not good
        document.querySelector("#error").innerHTML =
          "Picture quality is not good enough.";
        document.querySelector("#error").style.display = "block";
      } else {
        const source = { lon: data["lon"], lat: data["lat"] };
        draw_map(source);
      }
    })
    .then((_) => (switcher = 2))
    .catch((err) => console.error(err));
}

// this is called when the user want to predict image
// flow: called uploadImage() -> draw progress bar -> get API -> draw map
function predict() {
  document.querySelector("#p5js").style.display = "block";
  document.querySelector("#map").style.display = "none";
  document.querySelector("#error").style.display = "none";
  percentage = 0;

  const crs = document.querySelector("#crs").value;
  const ref = firebase.storage().ref();
  const file = document.querySelector("#photo").files[0];
  const name = uuid().substring(0, 9) + file.name;
  const metadata = { contentType: file.type };

  const task = ref.child(`images/${crs}-${name}`).put(file, metadata);
  task
    .then((snapshot) => snapshot.ref.getDownloadURL())
    .then((url) => {
      document.querySelector(".large-text").style.display = "none";
      document.querySelector("#so_hong_image").src = url;
    })
    .then((_) => {
      setup();
      switcher = 1;
      percentage = 1;
      successfullyGet(name);
    });
}
