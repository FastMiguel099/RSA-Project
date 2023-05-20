import numpy as np
import matplotlib.pyplot as plt

# Define the zone coordinates
zone = [(37.87694, -25.78116), (37.87091, -25.77317),
        (37.8703, -25.78948), (37.86342, -25.78214)]

# Rearrange the points to form a rectangle
sorted_zone = sorted(zone, key=lambda x: x[0]) # Sort points by latitude
bottom_points = sorted(sorted_zone[:2], key=lambda x: x[1]) # Sort the bottom two points by longitude
top_points = sorted(sorted_zone[2:], key=lambda x: x[1]) # Sort the top two points by longitude
rectangle_points = bottom_points + top_points[::-1] + [bottom_points[0]] # Create a closed rectangle path

# Find the bounding box (min and max latitudes and longitudes)
min_lat = min([point[0] for point in rectangle_points])
max_lat = max([point[0] for point in rectangle_points])
min_lon = min([point[1] for point in rectangle_points])
max_lon = max([point[1] for point in rectangle_points])

# Define the number of cells you want to divide the area into
n_lat = 10
n_lon = 10

# Create the grid lines for latitude and longitude
lat_lines = np.linspace(min_lat, max_lat, n_lat + 1)
lon_lines = np.linspace(min_lon, max_lon, n_lon + 1)

# Calculate the midpoints for latitude and longitude
lat_midpoints = (lat_lines[1:] + lat_lines[:-1]) / 2
lon_midpoints = (lon_lines[1:] + lon_lines[:-1]) / 2

# Plot the grid
fig, ax = plt.subplots()
ax.set_xlim(min_lon, max_lon)
ax.set_ylim(min_lat, max_lat)

for lat in lat_lines:
    ax.plot([min_lon, max_lon], [lat, lat], 'k-')

for lon in lon_lines:
    ax.plot([lon, lon], [min_lat, max_lat], 'k-')

# Create a rectangle (polygon) using the rearranged points
rectangle_points_array = np.array(rectangle_points)

ax.fill(rectangle_points_array[:, 1], rectangle_points_array[:, 0], 'c', alpha=0.5)

# Plot the middle point for each cell
for lat in lat_midpoints:
    for lon in lon_midpoints:
        ax.plot(lon, lat, 'bo')

plt.show()
