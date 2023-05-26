import threading, time, random
from shapely.geometry import Polygon
from geographiclib.geodesic import Geodesic
from auxiliar_functions import *
from driving import *

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

