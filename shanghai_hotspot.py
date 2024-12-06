import folium
from folium.plugins import HeatMap
from scipy.stats import gaussian_kde
import numpy as np
import pandas as pd
import json

# Step 1: Load metro station data from GeoJSON
geojson_path = 'TIL-4030-groupwork2/Shanghai_railwaystation.geojson'
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

# Extract metro station coordinates and names
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load bike-sharing data
file_path = 'TIL-4030-groupwork2/mobike_shanghai_sample_updated.csv'
bike_data = pd.read_csv(file_path)

# Extract start and end coordinates
start_coords = np.vstack([bike_data["start_location_x"], bike_data["start_location_y"]])
end_coords = np.vstack([bike_data["end_location_x"], bike_data["end_location_y"]])

# Step 3: Kernel Density Estimation (KDE) for start and end points
# KDE for start points
kde_start = gaussian_kde(start_coords)
x_min, x_max = start_coords[0].min(), start_coords[0].max()
y_min, y_max = start_coords[1].min(), start_coords[1].max()
x, y = np.linspace(x_min, x_max, 500), np.linspace(y_min, y_max, 500)
X_start, Y_start = np.meshgrid(x, y)
positions_start = np.vstack([X_start.ravel(), Y_start.ravel()])
density_start = kde_start(positions_start).reshape(X_start.shape)

# KDE for end points
kde_end = gaussian_kde(end_coords)
x_min, x_max = end_coords[0].min(), end_coords[0].max()
y_min, y_max = end_coords[1].min(), end_coords[1].max()
x, y = np.linspace(x_min, x_max, 500), np.linspace(y_min, y_max, 500)
X_end, Y_end = np.meshgrid(x, y)
positions_end = np.vstack([X_end.ravel(), Y_end.ravel()])
density_end = kde_end(positions_end).reshape(X_end.shape)

# Convert densities to heatmap data format
heat_data_start = np.vstack([X_start.ravel(), Y_start.ravel(), density_start.ravel()]).T
heat_data_start = heat_data_start[heat_data_start[:, 2] > 0]  # Filter low-density values

heat_data_end = np.vstack([X_end.ravel(), Y_end.ravel(), density_end.ravel()]).T
heat_data_end = heat_data_end[heat_data_end[:, 2] > 0]  # Filter low-density values

# Step 4: Create two interactive maps
# Map for start points
m_start = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="OpenStreetMap")
HeatMap(
    data=[[p[1], p[0], p[2]] for p in heat_data_start],
    max_zoom=16,
    radius=15,
).add_to(m_start)

# Add metro station markers to the start point map
for station in metro_stations:
    coordinates = station['coordinates']
    name = station['name']
    folium.Marker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [longitude, latitude]
        popup=name,
        icon=folium.Icon(color="blue", icon="train"),
    ).add_to(m_start)

# Save start point heatmap
m_start.save("shanghai_bike_start_heatmap.html")

# Map for end points
m_end = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="OpenStreetMap")
HeatMap(
    data=[[p[1], p[0], p[2]] for p in heat_data_end],
    max_zoom=16,
    radius=15,
).add_to(m_end)

# Add metro station markers to the end point map
for station in metro_stations:
    coordinates = station['coordinates']
    name = station['name']
    folium.Marker(
        location=[coordinates[1], coordinates[0]],
        popup=name,
        icon=folium.Icon(color="blue", icon="train"),
    ).add_to(m_end)

# Save end point heatmap
m_end.save("shanghai_bike_end_heatmap.html")

print("The heatmaps for start and end points have been saved as HTML files:")
print("- Start point heatmap: shanghai_bike_start_heatmap.html")
print("- End point heatmap: shanghai_bike_end_heatmap.html")