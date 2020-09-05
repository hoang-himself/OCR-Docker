function draw_map(coordinate) {
	var map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/mapbox/satellite-streets-v11',
		zoom: 18,
		//center: {lon: 106.58720175464157, lat: 10.95082750045397}
		center: coordinate
	});
	map.addControl(new mapboxgl.NavigationControl());
	var link = "https://api.mapbox.com/geocoding/v5/mapbox.places/";
	link += coordinate["lon"] + "," + coordinate["lat"] + ".json?access_token=";
	link += mapboxgl.accessToken;
	fetch(link)
	.then(response => response.json())
	.then(data => {
		const address = data.features[1].place_name;
		document.querySelector("#address").innerHTML = address;
	});
}
