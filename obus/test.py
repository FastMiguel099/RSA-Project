import numpy as np, threading, time, random
from shapely.geometry import Polygon
from geographiclib.geodesic import Geodesic

def find_closest_point(current_position, points):
    return min(points, key=lambda vertex: calculate_distance(current_position, vertex))

def calculate_distance(point1, point2):
    return Geodesic.WGS84.Inverse(point1[0], point1[1], point2[0], point2[1])['s12']

def navigate_to_point(start_point, destination_point,max_step_distance=10):
    geod = Geodesic.WGS84
    current_position = start_point
    
    while True:    
        result = geod.Inverse(*current_position, *destination_point)
        distance, bearing = result['s12'], result['azi1']
        step_distance = min(max_step_distance, distance)

        result = geod.Direct(*current_position, bearing, step_distance)
        current_position = (result['lat2'], result['lon2'])
        if (distance - step_distance) == 0:
            break

    return current_position
def reorder_points(points):
    min_lat_point = min(points, key=lambda x: x[0])
    max_lat_point = max(points, key=lambda x: x[0])
    
    points.remove(min_lat_point)
    points.remove(max_lat_point)

    min_lon_point = min(points, key=lambda x: x[1])
    max_lon_point = max(points, key=lambda x: x[1])

    return [min_lat_point, min_lon_point, max_lat_point, max_lon_point]

def create_grid(zone, resolution, zone_polygon):
    min_lat, min_lon = np.inf, np.inf
    max_lat, max_lon = -np.inf, -np.inf

    for point in zone:
        lat, lon = point
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lon = min(min_lon, lon)
        max_lon = max(max_lon, lon)

    lat_step = (max_lat - min_lat) / resolution
    lon_step = (max_lon - min_lon) / resolution

    lat_range = [min_lat + i * lat_step for i in range(resolution + 1)]
    lon_range = [min_lon + i * lon_step for i in range(resolution + 1)]

    grid = []
    centroids = []

    for i in range(resolution):
        for j in range(resolution):
            cell = [(lat_range[i], lon_range[j]), 
                    (lat_range[i + 1], lon_range[j]), 
                    (lat_range[i + 1], lon_range[j + 1]), 
                    (lat_range[i], lon_range[j + 1]),
                    (lat_range[i], lon_range[j])]

            cell_polygon = Polygon(cell)
            centroid = cell_polygon.centroid
            if not zone_polygon.contains(centroid):
                sub_resolution = 10
                sub_lat_step = lat_step / sub_resolution
                sub_lon_step = lon_step / sub_resolution

                flag = False
                for m in range(sub_resolution):
                    for n in range(sub_resolution):
                        sub_cell = [(lat_range[i] + m * sub_lat_step, lon_range[j] + n * sub_lon_step),
                                    (lat_range[i] + (m + 1) * sub_lat_step, lon_range[j] + n * sub_lon_step),
                                    (lat_range[i] + (m + 1) * sub_lat_step, lon_range[j] + (n + 1) * sub_lon_step),
                                    (lat_range[i] + m * sub_lat_step, lon_range[j] + (n + 1) * sub_lon_step),
                                    (lat_range[i] + m * sub_lat_step, lon_range[j] + n * sub_lon_step)]
                        sub_cell_polygon = Polygon(sub_cell)
                        sub_centroid = sub_cell_polygon.centroid
                        if zone_polygon.contains(sub_centroid):
                            grid.append(cell)
                            centroids.append((sub_centroid.x,sub_centroid.y))
                            flag = True
                            break
                    if flag:
                        break
            else:
                grid.append(cell)
                centroids.append((centroid.x,centroid.y))

    return grid, centroids

def find_closest_unclaimed_cell(device_id, current_position, centroids, claimed_centroids):
    unclaimed_centroids = [c for c in centroids if c not in claimed_centroids]
    if not unclaimed_centroids:
        return None

    closest_centroid = find_closest_point(current_position, unclaimed_centroids)
    claimed_centroids.append(closest_centroid)
    print(f"Device {device_id} claimed cell {closest_centroid}")
    return closest_centroid

def device_routine(device_id, start_position, centroids, claimed_centroids):
    current_position = start_position
    while True:
        closest_centroid = find_closest_unclaimed_cell(device_id, current_position, centroids, claimed_centroids)
        if closest_centroid is None:
            print(f"Device {device_id} finished patrolling")
            break

        # Simulate the time it takes for the device to move to the new cell
        time.sleep(random.uniform(0.1, 0.5))
        current_position = navigate_to_point(current_position, closest_centroid)


zone = reorder_points([(37.87694, -25.78116), (37.87091, -25.77317),
        (37.8703, -25.78948), (37.86342, -25.78214)])

resolution = 10
num_devices = 3
zone_polygon = Polygon(zone)
grid, centroids = create_grid(zone, resolution, zone_polygon)

# Assume your cells and their centroids are produced by create_grid
grid, centroids = create_grid(zone, resolution, zone_polygon)

# Assume you have a list of starting positions for the devices
device_positions = [(37.87091, -25.77317), (37.87694, -25.78116)]

claimed_centroids = []
for i, position in enumerate(device_positions):
    threading.Thread(target=device_routine, args=(i, position, centroids, claimed_centroids)).start()

