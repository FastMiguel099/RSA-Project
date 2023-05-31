var data = "";
var map;
var marker;

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
    if (marker) {
        map.removeLayer(marker);
    }
    
    marker = L.marker([response.boats[0].Latitude, response.boats[0].Longitude]).addTo(map);
    // Update JavaScript variables or elements as needed
    // Example: document.getElementById('result').innerText = response;
}

// Make the initial request
makeRequest();

// Set the interval for periodic requests (every 5 seconds in this example)
setInterval(makeRequest, 5000);


window.onload = function() {
    initMap();
}
