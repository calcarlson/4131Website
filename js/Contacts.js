var iconImg;
var pictures = ["haystacks", "legrandcanal", "starrynight", "sunrise", "sunsetativory", "thecliff", "womanwithaparasol", ];
var descriptions = ["Monet 1890", "Monet 1908", "Van Gogh 1889", "Monet 1872", "Guillaumin 1873", "Monet 1885", "Monet 1875", ];
var stopButton = document.getElementById('stop');
var map;
id = undefined;

markers = []
places = document.getElementById("places")

function pickImage() {
    var index = Math.floor(Math.random() * 7);
    iconImg.setAttribute("src", pictures[index] + ".png");
    iconImg.setAttribute("alt", descriptions[index]);
}

function start() {

    iconImg = document.getElementById("large");
    if (id == undefined) {
        id = setInterval(function() { pickImage(); }, 2000);
    }
}

function stop() {
    clearInterval(id);
}
stopButton.onclick = function() {
        stop();
        clearInterval(id);
    }
    //window.addEventListener("load", start, false);


function geolocate_destination(geocoder, originLatLng, destination, travel_mode) {
    console.log(destination)
    geocoder.geocode({ 'address': destination }, function(results, status) {

        if (status == google.maps.GeocoderStatus.OK) {
            var request = {
                origin: originLatLng,
                destination: results[0].geometry.location,
                travelMode: travel_mode
            };
            console.log(request)

            directionsService.route(request, function(response, status) {
                console.log(status)
                if (status == 'OK') {
                    directionsRenderer.setDirections(response)
                }
            });
        } else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    })
}

function createMarker(place) {
    var marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location
    })

    markers.push(marker)

    infowindow = new google.maps.InfoWindow();

    google.maps.event.addListener(marker, 'click', function() {
        infowindow.setContent(place.name)
        infowindow.open(map, this)
    })

    google.maps.event.addListener(marker, 'mouseover', function() {
        infowindow.setContent(place.name);
        infowindow.open(map, this)
    })
}

function calcRoute(position) {
    //clear_place_markers()
    var transit_radio = document.getElementsByClassName('nav_rad');
    geolocated = new google.maps.LatLng(position.coords.latitude, position.coords.longitude)

    var selectedMode = null

    for (radio of transit_radio) {
        if (radio.checked) {
            selectedMode = radio.value
        }
    }

    var geocoder = new google.maps.Geocoder()
    var geocoder_destination = new google.maps.Geocoder()
    var destination = document.getElementById("directions").value

    if (selectedMode != null) {
        console.log(destination)
        geolocate_destination(geocoder, geolocated, destination, google.maps.TravelMode[selectedMode])
    } else {
        alert("Please Select a Mode of Transport")
    }

}

function initMap() {
    directionsService = new google.maps.DirectionsService()
    directionsRenderer = new google.maps.DirectionsRenderer()
    var addresses = document.getElementsByClassName('contactaddress')
    var rows = document.getElementsByClassName('contactrow')
    var geocoder = new google.maps.Geocoder()

    var table = document.getElementById('contacts')
    var name;

    map = new google.maps.Map(document.getElementById('map'), {
        center: {
            lat: 44.9727,
            lng: -93.23540000000003
        },
        zoom: 15,

        //JSON code provided by google API to custom style the google map
        styles: [{
            "elementType": "geometry",
            "stylers": [{
                "color": "#f5f5f5"
            }]
        }, {
            "elementType": "labels.icon",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#616161"
            }]
        }, {
            "elementType": "labels.text.stroke",
            "stylers": [{
                "color": "#f5f5f5"
            }]
        }, {
            "featureType": "administrative.land_parcel",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#bdbdbd"
            }]
        }, {
            "featureType": "poi",
            "elementType": "geometry",
            "stylers": [{
                "color": "#eeeeee"
            }]
        }, {
            "featureType": "poi",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#757575"
            }]
        }, {
            "featureType": "poi.park",
            "elementType": "geometry",
            "stylers": [{
                "color": "#e5e5e5"
            }]
        }, {
            "featureType": "poi.park",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#9e9e9e"
            }]
        }, {
            "featureType": "road",
            "elementType": "geometry",
            "stylers": [{
                "color": "#ffffff"
            }]
        }, {
            "featureType": "road.arterial",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#757575"
            }]
        }, {
            "featureType": "road.highway",
            "elementType": "geometry",
            "stylers": [{
                "color": "#dadada"
            }]
        }, {
            "featureType": "road.highway",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#616161"
            }]
        }, {
            "featureType": "road.local",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#9e9e9e"
            }]
        }, {
            "featureType": "transit.line",
            "elementType": "geometry",
            "stylers": [{
                "color": "#e5e5e5"
            }]
        }, {
            "featureType": "transit.station",
            "elementType": "geometry",
            "stylers": [{
                "color": "#eeeeee"
            }]
        }, {
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [{
                "color": "#c9c9c9"
            }]
        }, {
            "featureType": "water",
            "elementType": "labels.text.fill",
            "stylers": [{
                "color": "#9e9e9e"
            }]
        }]
    });
    for (var i = 1, row; row = table.rows[i]; i++) {
        for (var j = 0, col; col = row.cells[j]; j++) {
            if (j == 0) {
                name = col.innerHTML
            }

            if (j == 2) {
                geolocate_marker(map, geocoder, name, col.innerHTML)
            }
        }
    }

    directionsRenderer.setMap(map);
    directionsRenderer.setPanel(document.getElementById('panel_directions'));

}


function createMarker(place) {
    var marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location
    })

    markers.push(marker)

    infowindow = new google.maps.InfoWindow();

    google.maps.event.addListener(marker, 'click', function() {
        infowindow.setContent(place.name)
        infowindow.open(map, this)
    })

    google.maps.event.addListener(marker, 'mouseover', function() {
        infowindow.setContent(place.name);
        infowindow.open(map, this)
    })
}

function callback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            createMarker(results[i])
        }
    }
}

function getCurrentLocation() {

    document.getElementById('directions').style.opacity = 1

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(calcRoute);
    } else {
        showError(x.innerHTML = "Geolocation not supported.")
    }
}

function place_changer() {
    //clear_place_markers()

    if (places.value == "other") {

        search_place = other.value

        var request = {
            location: centerLatLng,
            query: search_place
        };

        service = new google.maps.places.PlacesService(map)
        service.textSearch(request, callback)

    } else {
        other.value = ""
        find_place = places.value

        var request = {
            location: centerLatLng,
            radius: parseInt(range_input.value),
            type: [find_place]
        };

        service = new google.maps.places.PlacesService(map)
        service.nearbySearch(request, callback)
    }

}

function geolocate_marker(map, geocoder, name, address) {
    geocoder.geocode({ 'address': address }, function(results, status) {

        if (status == google.maps.GeocoderStatus.OK) {
            var marker = new google.maps.Marker({
                position: results[0].geometry.location,
                map: map,
                //icon: marker_icon,
                animation: google.maps.Animation.DROP,
            })

            markers.push(marker)

            var contentDisp =
                '<div>' +
                '<p style="font-weight:italic">' +
                name + '</p>' + '<p>' + address.split('<br>')[0] + '</p>' + '</div>';

            var infowindow = new google.maps.InfoWindow({
                content: contentDisp
            });

            marker.addListener('click', function() {
                infowindow.open(map, marker)
            })
        } else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    })
}