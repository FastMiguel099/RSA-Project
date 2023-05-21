import numpy as np
from shapely.geometry import Polygon, Point
from haversine import haversine, Unit
import matplotlib.pyplot as plt
import math

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

def angle(start, end):
    delta_lat = end[0] - start[0]
    delta_lon = end[1] - start[1]
    angle = math.atan2(delta_lat, delta_lon)
    return angle

def assign_cells(grid, centroids, num_devices):
    device_cells = [[] for _ in range(num_devices)]
    device_centroids = [[] for _ in range(num_devices)]

    start_centroid = centroids[0]

    # Exclude the first cell (already used as starting point)
    remaining_centroids = centroids[1:]
    remaining_grid = grid[1:]

    # Sort centroids based on their angles relative to the starting point
    sorted_centroids = sorted(remaining_centroids, key=lambda c: angle(start_centroid, c))
    sorted_grid = [cell for _, cell in sorted(enumerate(remaining_grid), key=lambda idx_cell: angle(start_centroid, remaining_centroids[idx_cell[0]]))]

    # Divide the sorted centroids into sections and assign each section to a device
    section_size = len(sorted_centroids) // num_devices
    for device_id in range(num_devices):
        start_index = device_id * section_size
        end_index = start_index + section_size if device_id < num_devices - 1 else len(sorted_centroids)
        device_centroids[device_id] = [start_centroid] + sorted_centroids[start_index:end_index]
        device_cells[device_id] = [grid[0]] + sorted_grid[start_index:end_index]

    return device_cells, device_centroids

def generate_paths(device_centroids):
    device_paths = []

    for centroids in device_centroids:
        path = []
        for centroid in centroids:
            path.append((centroid[0], centroid[1]))
        device_paths.append(path)

    return device_paths

def calculate_resolution(zone, visibility_radius):
    latitudes, longitudes = zip(*zone)
    min_lat, max_lat, min_lon, max_lon = min(latitudes), max(latitudes), min(longitudes), max(longitudes)
    
    lat_distance = haversine((min_lat, min_lon), (max_lat, min_lon), unit=Unit.METERS)
    lon_distance = haversine((min_lat, min_lon), (min_lat, max_lon), unit=Unit.METERS)
    
    visible_diameter = 2 * visibility_radius
    
    lat_resolution = int(lat_distance / visible_diameter)
    lon_resolution = int(lon_distance / visible_diameter)

    return max(lat_resolution, lon_resolution)

def visualize_paths(zone, grid, device_paths):
    fig, ax = plt.subplots()

    colors = ['r', 'g', 'b']  # You can add more colors if you have more devices

    # Plot device paths
    for i, path in enumerate(device_paths):
        latitudes, longitudes = zip(*path)
        ax.plot(longitudes, latitudes, marker='o', linestyle='-', color=colors[i], label=f'Device {i + 1}')

    # Plot zone
    zone_latitudes, zone_longitudes = zip(*(zone + [zone[0]]))
    ax.plot(zone_longitudes, zone_latitudes, marker='o', linestyle='-', color='k', label='Zone')

    # Plot grid cells
    for cell in grid:
        cell_latitudes, cell_longitudes = zip(*(cell + [cell[0]]))
        ax.plot(cell_longitudes, cell_latitudes, marker='', linestyle='-', color='gray', linewidth=0.5, alpha=0.5)

    latitudes, longitudes = zip(*zone)
    min_lat, max_lat, min_lon, max_lon = min(latitudes), max(latitudes), min(longitudes), max(longitudes)
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Paths for each device with zone and grid")
    plt.legend()
    plt.show()


zone = [(37.87694, -25.78116), (37.87091, -25.77317),
        (37.8703, -25.78948), (37.86342, -25.78214)]

zone = reorder_points(zone)

visibility_radius = 50  # 100 meters of radius
resolution = calculate_resolution(zone, visibility_radius)
num_devices = 3
zone_polygon = Polygon(zone)
grid, centroids = create_grid(zone, resolution, zone_polygon)
device_cells, device_centroids = assign_cells(grid, centroids, num_devices)

device_paths = generate_paths(device_centroids)

visualize_paths(zone, grid,device_paths)