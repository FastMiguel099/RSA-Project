import numpy as np
from shapely.geometry import Polygon
from sklearn.cluster import KMeans
from geographiclib.geodesic import Geodesic

def find_closest_point(current_position, points):
    return min(points, key=lambda vertex: calculate_distance(current_position, vertex))

def calculate_distance(point1, point2):
    return Geodesic.WGS84.Inverse(point1[0], point1[1], point2[0], point2[1])['s12']


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

def assign_cells(grid, centroids, num_devices):
    kmeans = KMeans(n_clusters=num_devices, random_state=0).fit(centroids)
    device_cells = [[] for _ in range(num_devices)]
    device_centroids = [[] for _ in range(num_devices)]
    
    for i, (cell, centroid) in enumerate(zip(grid, centroids)):
        device_id = kmeans.predict([centroid])[0]
        device_cells[device_id].append(cell)
        device_centroids[device_id].append(centroid)

    return device_cells, device_centroids

def generate_paths(device_centroids):
    device_paths = []
    start_point = (37.86497, -25.78921)
    for centroids in device_centroids:
        path = []
        current_position = find_closest_point(start_point, centroids)
        while centroids:
            closest_centroid = find_closest_point(current_position, centroids)
            path.append(closest_centroid)
            centroids.remove(closest_centroid)
            current_position = closest_centroid
        path = two_opt(path)  # use 2-opt to find a better path
        device_paths.append(path)
    return device_paths

def two_opt_swap(path, i, k):
    """ Reverse the order of the nodes between i and k in the path. """
    return path[:i] + path[i:k+1][::-1] + path[k+1:]

def two_opt(path):
    """ Implement 2-opt to find a better path. """
    best_path = path
    best_distance = calculate_total_distance(path)

    improved = True
    while improved:
        improved = False
        for i in range(1, len(path) - 1):
            for k in range(i+1, len(path)):
                new_path = two_opt_swap(best_path, i, k)
                new_distance = calculate_total_distance(new_path)
                if new_distance < best_distance:
                    best_distance = new_distance
                    best_path = new_path
                    improved = True

    return best_path

def calculate_total_distance(path):
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += calculate_distance(path[i], path[i + 1])
    return total_distance
