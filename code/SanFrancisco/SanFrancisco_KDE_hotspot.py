import folium
from scipy.stats import gaussian_kde
import numpy as np
import pandas as pd
import json

# Step 1: Load GeoJSON data for metro stations
geojson_path = 'TIL-4030-groupwork2/data/SanFrancisco/SanFrancisco_railwaystation.geojson' 
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

# Extract metro station coordinates
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load bike-sharing data
file_path = 'TIL-4030-groupwork2/data/SanFrancisco/202008-baywheels-tripdata.csv' 

# Load bike-sharing data into a DataFrame
bike_data = pd.read_csv(file_path)

# Filter data within the bounding box
lng_min, lng_max = -122.5233, -122.3551
lat_min, lat_max = 37.7083, 37.8163

filtered_data = bike_data[
    (bike_data["start_lng"] >= lng_min) & (bike_data["start_lng"] <= lng_max) &
    (bike_data["end_lng"] >= lng_min) & (bike_data["end_lng"] <= lng_max) &
    (bike_data["end_lat"] >= lat_min) & (bike_data["end_lat"] <= lat_max)
]

# Extract start and end coordinates
start_coords = np.vstack([filtered_data["start_lng"], filtered_data["end_lat"]])  # [lng, lat]
end_coords = np.vstack([filtered_data["end_lng"], filtered_data["end_lat"]])     # [lng, lat]

# Step 3: KDE for density calculation
# Define grid resolution and bandwidth
lng_grid = np.linspace(lng_min, lng_max, 500)
lat_grid = np.linspace(lat_min, lat_max, 500)
X, Y = np.meshgrid(lng_grid, lat_grid)
grid_coords = np.vstack([X.ravel(), Y.ravel()])

# KDE for start points
bandwidth_start = 0.03  # Adjust bandwidth value to optimize smoothing effect
kde_start = gaussian_kde(start_coords, bw_method=bandwidth_start)(grid_coords).reshape(X.shape)

# KDE for end points
bandwidth_end = 0.03
kde_end = gaussian_kde(end_coords, bw_method=bandwidth_end)(grid_coords).reshape(X.shape)

# Normalize KDE values
kde_start_norm = (kde_start - kde_start.min()) / (kde_start.max() - kde_start.min())
kde_end_norm = (kde_end - kde_end.min()) / (kde_end.max() - kde_end.min())

# Step 4: Draw heatmaps separately
# Custom color gradient
gradient = {
    0.1: 'blue',     # Low-density area
    0.3: 'lime',
    0.6: 'yellow',
    1.0: 'red'       # High-density area
}

# Create heatmap for start points
m_start = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="CartoDB positron")

# Add KDE heatmap for start points
for i in range(len(lng_grid) - 1):
    for j in range(len(lat_grid) - 1):
        intensity = kde_start_norm[j, i]
        if intensity > 0:  # Only add non-zero density areas
            folium.Rectangle(
                bounds=[[lat_grid[j], lng_grid[i]], [lat_grid[j + 1], lng_grid[i + 1]]],
                color=None,
                fill=True,
                fill_color=f'rgba(255, 0, 0, {intensity})',
                fill_opacity=intensity
            ).add_to(m_start)

# Add metro station markers to start point map
for station in metro_stations:
    coordinates = station['coordinates']
    name = station['name']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [lng, lat]
        radius=3,
        color='purple',
        fill=True,
        fill_opacity=0.9,
        popup=name
    ).add_to(m_start)

# Save start points map
m_start.save("sf_bike_start_heatmap_kde.html")
print("Start heatmap saved as 'sf_bike_start_heatmap_kde.html'")

# Create heatmap for end points
m_end = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="CartoDB positron")

# Add KDE heatmap for end points
for i in range(len(lng_grid) - 1):
    for j in range(len(lat_grid) - 1):
        intensity = kde_end_norm[j, i]
        if intensity > 0:  # Only add non-zero density areas
            folium.Rectangle(
                bounds=[[lat_grid[j], lng_grid[i]], [lat_grid[j + 1], lng_grid[i + 1]]],
                color=None,
                fill=True,
                fill_color=f'rgba(255, 0, 0, {intensity})',
                fill_opacity=intensity
            ).add_to(m_end)

# Add metro station markers to end point map
for station in metro_stations:
    coordinates = station['coordinates']
    name = station['name']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [lng, lat]
        radius=3,
        color='purple',
        fill=True,
        fill_opacity=0.9,
        popup=name
    ).add_to(m_end)

# Save end points map
m_end.save("sf_bike_end_heatmap_kde.html")
print("End heatmap saved as 'sf_bike_end_heatmap_kde.html'")