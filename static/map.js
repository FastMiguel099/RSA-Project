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


for (var marker of initialMarkers) {
    L.marker(marker, {icon: markerIcon}).addTo(map).bindTooltip(marker.toString(), {permanent: false});
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

var markers = [];
/*
let resolution = 10;  

let {grid, centroids} = createGrid(reorderPoints(initialMarkers), resolution, polygon.toGeoJSON());


// Add grid to the map
grid.forEach(cell => {
    let swappedCell = cell.map(coord => [coord[1], coord[0]]);
    L.polygon(swappedCell, { color: 'blue' }).addTo(map);
});

console.log(centroids.length);
// Add centroids to the map
centroids.forEach(centroid => {
    L.marker(centroid).addTo(map);
});
*/
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

/*
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
            let cell = [
                [lon_range[j], lat_range[i]],
                [lon_range[j], lat_range[i + 1]],
                [lon_range[j + 1], lat_range[i + 1]],
                [lon_range[j + 1], lat_range[i]],
                [lon_range[j], lat_range[i]]
            ];
            let cellPolygon = turf.polygon([cell]);
            let centroid = turf.centroid(cellPolygon);

            if (!turf.booleanPointInPolygon(centroid, zone_polygon)) {
                let subResolution = 10;
                let subLatStep = lat_step / subResolution;
                let subLonStep = lon_step / subResolution;
                outer: for (let m = 0; m < subResolution; m++) {
                    for (let n = 0; n < subResolution; n++) {
                        let subCell = [
                            [lon_range[j] + n * subLonStep, lat_range[i] + m * subLatStep],
                            [lon_range[j] + n * subLonStep, lat_range[i] + (m + 1) * subLatStep],
                            [lon_range[j] + (n + 1) * subLonStep, lat_range[i] + (m + 1) * subLatStep],
                            [lon_range[j] + (n + 1) * subLonStep, lat_range[i] + m * subLatStep],
                            [lon_range[j] + n * subLonStep, lat_range[i] + m * subLatStep]
                        ];
                        let subCellPolygon = turf.polygon([subCell]);
                        let subCentroid = turf.centroid(subCellPolygon);
                        if (turf.booleanPointInPolygon(subCentroid, zone_polygon)) {
                            grid.push(cell);
                            centroids.push([subCentroid.geometry.coordinates[1], subCentroid.geometry.coordinates[0]]);
                            break outer;
                        }
                    }
                }
            }
            else{
                grid.push(cell);
                centroids.push([centroid.geometry.coordinates[1], centroid.geometry.coordinates[0]]);
            }
        }
    }

    return {grid, centroids};
}
*/

/*
$(document).ready(function () {
    setInterval(obuCall, 1000);
});
*/