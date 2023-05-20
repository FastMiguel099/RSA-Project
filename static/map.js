var map = L.map('map').setView([37.8703925, -25.7814875], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var obuIcon = L.icon({
    iconUrl: "static/boat.png",
    iconSize: [16, 16],
    iconAnchor: [18, 39],
    popupAnchor: [10, -35]
});

var markerIcon = L.icon({
    iconUrl: "static/marker.png",
    iconSize: [16, 16],
    iconAnchor: [18, 39],
    popupAnchor: [10, -35]
});

var initialMarkers = [
    [37.87694, -25.78116],
    [37.87091, -25.77317],
    [37.8703, -25.78948],
    [37.86342, -25.78214]
];

var polygon = L.polygon(reorderPoints(initialMarkers), {color: 'red', fill: false}).addTo(map);

var markers = [];

let resolution = 10;  

let {grid, centroids} = createGrid(reorderPoints(initialMarkers), resolution, polygon.toGeoJSON());


// Add grid to the map
grid.forEach(cell => {
    let swappedCell = cell.map(coord => [coord[1], coord[0]]);
    L.polygon(swappedCell, { color: 'blue' }).addTo(map);
});


// Add centroids to the map
centroids.forEach(centroid => {
    let lat = centroid[1];
    let lon = centroid[0];
    L.marker([lat, lon]).addTo(map);
});

function obuCall() {
    $(document).ready(function(){

        $.ajax({
            url: '',
            type: 'get',
            contentType: 'application/json',
            dataType: 'json',
            success: function(response){
                markers.forEach(delMarker)
                let i=0;
                for(var key in response){
                    markers[i] = L.marker([ response[key]["latitude"], response[key]["longitude"]], {icon: obuIcon}).addTo(map).bindTooltip(key, {permanent: false});
                    i++;
                } 
            }
        })

    })
}

function delMarker(value, index, array){
    map.removeLayer(value)
}

function reorderPoints(points) {
    let minLatPoint = null;
    let maxLatPoint = null;
    let minLonPoint = null;
    let maxLonPoint = null;

    points.forEach(point => {
        let [lat, lon] = point;

        if (!minLatPoint || lat < minLatPoint[0]) {
            minLatPoint = point;
        }

        if (!maxLatPoint || lat > maxLatPoint[0]) {
            maxLatPoint = point;
        }

        if (!minLonPoint || lon < minLonPoint[1]) {
            minLonPoint = point;
        }

        if (!maxLonPoint || lon > maxLonPoint[1]) {
            maxLonPoint = point;
        }
    });

    points = points.filter(point => point !== minLatPoint && point !== maxLatPoint && point !== minLonPoint && point !== maxLonPoint);

    if (points.length > 0) {
        maxLonPoint = points[0];
    }

    return [minLatPoint, minLonPoint, maxLatPoint, maxLonPoint];
}


function createGrid(zone, resolution, zone_polygon) {
    let min_lat = Infinity, min_lon = Infinity, max_lat = -Infinity, max_lon = -Infinity;

    zone.forEach(point => {
        let [lat, lon] = point;
        min_lat = Math.min(min_lat, lat);
        max_lat = Math.max(max_lat, lat);
        min_lon = Math.min(min_lon, lon);
        max_lon = Math.max(max_lon, lon);
    });

    const lat_step = (max_lat - min_lat) / resolution;
    const lon_step = (max_lon - min_lon) / resolution;

    let lat_range = Array.from({length: resolution + 1}, (_, i) => min_lat + i * lat_step);
    let lon_range = Array.from({length: resolution + 1}, (_, i) => min_lon + i * lon_step);

    let grid = [];
    let centroids = [];

    for (let i = 0; i < resolution; i++) {
        for (let j = 0; j < resolution; j++) {
            const processCell = (lon_start, lon_end, lat_start, lat_end) => {
                let cell = [
                    [lon_start, lat_start],
                    [lon_start, lat_end],
                    [lon_end, lat_end],
                    [lon_end, lat_start],
                    [lon_start, lat_start]
                ];

                let cellPolygon = turf.polygon([cell]);
                let centroid = turf.centroid(cellPolygon);

                if (turf.booleanPointInPolygon(centroid, zone_polygon)) {
                    grid.push(cell);
                    centroids.push([centroid.geometry.coordinates[0], centroid.geometry.coordinates[1]]);
                    return true;
                }
                return false;
            }

            if (!processCell(lon_range[j], lon_range[j + 1], lat_range[i], lat_range[i + 1])) {
                let subResolution = 10;
                let subLatStep = lat_step / subResolution;
                let subLonStep = lon_step / subResolution;

                for (let m = 0; m < subResolution; m++) {
                    for (let n = 0; n < subResolution; n++) {
                        if (processCell(
                            lon_range[j] + n * subLonStep,
                            lon_range[j] + (n + 1) * subLonStep,
                            lat_range[i] + m * subLatStep,
                            lat_range[i] + (m + 1) * subLatStep)) {
                            break;
                        }
                    }
                }
            }
        }
    }

    return {grid, centroids};
}

$(document).ready(function () {
    setInterval(obuCall, 1000);
});
