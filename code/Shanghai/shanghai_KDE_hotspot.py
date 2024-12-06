import folium
from scipy.stats import gaussian_kde
import numpy as np
import pandas as pd
import json

# Step 1: Load Metro Station Data
geojson_path = 'TIL-4030-groupwork2/data/Shanghai/Shanghai_railwaystation.geojson'
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

# Extract metro station coordinates
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load Bike-Sharing Data
file_path = 'TIL-4030-groupwork2/data/Shanghai/mobike_shanghai_sample_updated.csv'
bike_data = pd.read_csv(file_path)

# Extract start and end coordinates
start_coords = np.vstack([bike_data["start_location_x"], bike_data["start_location_y"]])  # [lon, lat]
end_coords = np.vstack([bike_data["end_location_x"], bike_data["end_location_y"]])      # [lon, lat]

# Step 3: Compute KDE for Start and End Points
# Define grid resolution and bandwidth
x_min, x_max = min(start_coords[0].min(), end_coords[0].min()), max(start_coords[0].max(), end_coords[0].max())
y_min, y_max = min(start_coords[1].min(), end_coords[1].min()), max(start_coords[1].max(), end_coords[1].max())

# Set grid resolution (1000x1000)
x_grid = np.linspace(x_min, x_max, 1000)
y_grid = np.linspace(y_min, y_max, 1000)
X, Y = np.meshgrid(x_grid, y_grid)
grid_coords = np.vstack([X.ravel(), Y.ravel()])

# KDE for start points
bandwidth_start = 0.03
kde_start = gaussian_kde(start_coords, bw_method=bandwidth_start)(grid_coords).reshape(X.shape)

# KDE for end points
bandwidth_end = 0.03
kde_end = gaussian_kde(end_coords, bw_method=bandwidth_end)(grid_coords).reshape(X.shape)

# Normalize KDE values
kde_start_norm = (kde_start - kde_start.min()) / (kde_start.max() - kde_start.min())
kde_start_norm = np.power(kde_start_norm, 0.7)  # Enhance contrast

kde_end_norm = (kde_end - kde_end.min()) / (kde_end.max() - kde_end.min())
kde_end_norm = np.power(kde_end_norm, 0.7)  # Enhance contrast

# Step 4: Draw Heatmaps Separately
# Custom color gradient
gradient = {
    0.1: 'blue',     # Low density area
    0.3: 'lime',
    0.6: 'yellow',
    1.0: 'red'       # High density area
}

# Create heatmap for start points
m_start = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="CartoDB positron")

# Add KDE heatmap for start points
for i in range(len(x_grid) - 1):
    for j in range(len(y_grid) - 1):
        intensity = kde_start_norm[j, i]
        if intensity > 0:  # Only add non-zero density areas
            folium.Rectangle(
                bounds=[[y_grid[j], x_grid[i]], [y_grid[j + 1], x_grid[i + 1]]],
                color=None,
                fill=True,
                fill_color=f'rgba(255, 0, 0, {intensity})',
                fill_opacity=intensity  # Set opacity based on intensity
            ).add_to(m_start)

# Add metro station markers to start point map
for station in metro_stations:
    coordinates = station['coordinates']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [lon, lat]
        radius=3,
        color='purple',
        fill=True,
        fill_opacity=0.9,
    ).add_to(m_start)

# Save start points map
m_start.save("shanghai_bike_start_heatmap_kde.html")
print("Start heatmap saved as 'shanghai_bike_start_heatmap_kde.html'")

# Create heatmap for end points
m_end = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="CartoDB positron")

# Add KDE heatmap for end points
for i in range(len(x_grid) - 1):
    for j in range(len(y_grid) - 1):
        intensity = kde_end_norm[j, i]
        if intensity > 0:  # Only add non-zero density areas
            folium.Rectangle(
                bounds=[[y_grid[j], x_grid[i]], [y_grid[j + 1], x_grid[i + 1]]],
                color=None,
                fill=True,
                fill_color=f'rgba(255, 0, 0, {intensity})',
                fill_opacity=intensity  # Set opacity based on intensity
            ).add_to(m_end)

# Add metro station markers to end point map
for station in metro_stations:
    coordinates = station['coordinates']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [lon, lat]
        radius=3,
        color='purple',
        fill=True,
        fill_opacity=0.9,
    ).add_to(m_end)

# Save end points map
m_end.save("shanghai_bike_end_heatmap_kde.html")
print("End heatmap saved as 'shanghai_bike_end_heatmap_kde.html'")