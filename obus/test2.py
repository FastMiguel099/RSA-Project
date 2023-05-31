from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from auxiliar_functions import *

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

zone = [(37.87400, -25.78800), (37.87400, -25.77800), (37.8640, -25.77800), (37.86400, -25.78800)]

zone = reorder_points(zone)
resolution = 10
num_devices = 3
zone_polygon = Polygon(zone)
grid, centroids = create_grid(zone, resolution, zone_polygon)

device_cells, device_centroids = assign_cells(grid, centroids, num_devices)

# Generate the initial paths
device_paths = generate_paths(device_centroids)

visualize_paths(zone, grid, device_paths)