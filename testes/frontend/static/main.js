var map;
var marker1, marker2, marker3;
var polyline1, polyline2, polyline3;
var path1 = [];
var path2 = [];
var path3 = [];
var first = true;

function initMap(){
    map = L.map('map').setView([37.8690, -25.7830], 15);
    //map.fitBounds(polygon.getBounds());
    
    // Add a tile layer (e.g., OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18,
        }).addTo(map);

    // marker2 = L.marker([37.87400, -25.78800]).addTo(map);
    var polygon = L.polygon([
        [37.87400, -25.78800],
        [37.87400, -25.77800],
        [37.86400, -25.77800],
        [37.86400, -25.78800]
    ]).addTo(map);
}

// Function to make the AJAX request
function makeRequest() {
    $.ajax({
        url: "/get_data",
        method: "GET",
        dataType: "json",
        success: function(response) {
            // maybe check if boats have moved?
            // if response is the same as the previous maybe do not call updateLocations()?

            updateLocations(response);
        },
        error: function(xhr, status, error) {
            console.log("AJAX request failed:", error);
        }
    });
}

function updateLocations(response) {
    // Perform actions with the received data
    console.log("New data received:", response);
    console.log(response);


    //remove old marker
    if (marker1) {
        map.removeLayer(marker1);
    }

    // for (boat of response.boats){
    //     if (boat.latitude==0){
    //         return;
    //     }
    // }
    
    if(first){
        marker1 = L.marker([response.boats[0].latitude, response.boats[0].longitude]).addTo(map);
        marker2 = L.marker([response.boats[1].latitude, response.boats[1].longitude]).addTo(map);
        marker3 = L.marker([response.boats[2].latitude, response.boats[1].longitude]).addTo(map);
        first=false;
    }

    if(response.boats[0].latitude!=0){

    path1.push([response.boats[0].latitude, response.boats[0].longitude]);
    }
    if(response.boats[1].latitude!=0){

    path2.push([response.boats[1].latitude, response.boats[1].longitude]);
    }
    if(response.boats[2].latitude!=0){

    path3.push([response.boats[2].latitude, response.boats[2].longitude]);
    }

    
    polyline1 = L.polyline(path1, { color: 'blue' }).addTo(map);
    polyline2 = L.polyline(path2, { color: 'red' }).addTo(map);
    polyline3 = L.polyline(path3, { color: 'green' }).addTo(map);
}

// Make the initial request
makeRequest();

// Set the interval for periodic requests 
setInterval(makeRequest, 400);


window.onload = function() {
    initMap();
}
