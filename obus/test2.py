import numpy as np
from shapely.geometry import Polygon
from haversine import haversine, Unit
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

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
            def process_cell(lon_start, lon_end, lat_start, lat_end):
                cell = [(lon_start, lat_start), (lon_start, lat_end), 
                        (lon_end, lat_end), (lon_end, lat_start), 
                        (lon_start, lat_start)]
                cell_polygon = Polygon(cell)
                centroid = cell_polygon.centroid

                if zone_polygon.contains(centroid):
                    grid.append(cell)
                    centroids.append((centroid.x, centroid.y))
                    return True
                return False

            if not process_cell(lon_range[j], lon_range[j + 1], lat_range[i], lat_range[i + 1]):
                sub_resolution = 10
                sub_lat_step = lat_step / sub_resolution
                sub_lon_step = lon_step / sub_resolution

                for m in range(sub_resolution):
                    for n in range(sub_resolution):
                        if process_cell(lon_range[j] + n * sub_lon_step,
                                        lon_range[j] + (n + 1) * sub_lon_step,
                                        lat_range[i] + m * sub_lat_step,
                                        lat_range[i] + (m + 1) * sub_lat_step):
                            break

    return grid,centroids

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