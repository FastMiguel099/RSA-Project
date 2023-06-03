var map;
var marker1, marker2, marker3;
var polyline1, polyline2, polyline3;
var path1 = [];
var path2 = [];
var path3 = [];
var prev_lat1 = 0.0;
var prev_lon1 = 0.0;
var prev_lat2 = 0.0;
var prev_lon2 = 0.0;
var prev_lat3 = 0.0;
var prev_lon3 = 0.0;
var first1 = true;
var first2 = true;
var first3 = true;

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

    if(response.boats[0].latitude!=0){
        if(first1){
            marker1 = L.marker([response.boats[0].latitude, response.boats[0].longitude]);
            first1=false;
        }
        if(response.boats[0].latitude !== prev_lat1 || response.boats[0].longitude !== prev_lon1){
            path1.push([response.boats[0].latitude, response.boats[0].longitude]);
            prev_lat1=response.boats[0].latitude;
            prev_lon1=response.boats[0].longitude;
        }
    }

    if(response.boats[1].latitude!=0){
        if(first2){
            marker1 = L.marker([response.boats[1].latitude, response.boats[1].longitude]);
            first2=false;
        }
        if(response.boats[1].latitude !== prev_lat2 || response.boats[1].longitude !== prev_lon2){
            path2.push([response.boats[1].latitude, response.boats[1].longitude]);
            prev_lat2=response.boats[1].latitude;
            prev_lon2=response.boats[1].longitude;
        }
    }

    if(response.boats[2].latitude!=0){
        if(first3){
            marker1 = L.marker([response.boats[2].latitude, response.boats[2].longitude]);
            first3=false;
        }
        if(response.boats[2].latitude !== prev_lat3 || response.boats[2].longitude !== prev_lon3){
            path3.push([response.boats[2].latitude, response.boats[2].longitude]);
            prev_lat3=response.boats[2].latitude;
            prev_lon3=response.boats[2].longitude;
        }
    }

    
    polyline1 = L.polyline(path1, { color: 'blue' }).addTo(map);
    polyline2 = L.polyline(path2, { color: 'red' }).addTo(map);
    polyline3 = L.polyline(path3, { color: 'green' }).addTo(map);
}

// Make the initial request
makeRequest();

// Set the interval for periodic requests 
setInterval(makeRequest, 150);


window.onload = function() {
    initMap();
}
