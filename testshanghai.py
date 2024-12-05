import folium
from scipy.stats import gaussian_kde
import numpy as np
import pandas as pd
import json

# Step 1: Load Metro Station Data
geojson_path = 'TIL-4030-groupwork2/Shanghai_railwaystation.geojson'
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

# Extract metro station coordinates
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load Bike-Sharing Data
file_path = 'TIL-4030-groupwork2/mobike_shanghai_sample_updated.csv'
bike_data = pd.read_csv(file_path)

# Extract start and end coordinates
start_coords = np.vstack([bike_data["start_location_x"], bike_data["start_location_y"]])  # [lon, lat]
end_coords = np.vstack([bike_data["end_location_x"], bike_data["end_location_y"]])      # [lon, lat]

# Step 3: Compute KDE for Start and End Points
# Define the grid for KDE
x_min, x_max = min(start_coords[0].min(), end_coords[0].min()), max(start_coords[0].max(), end_coords[0].max())
y_min, y_max = min(start_coords[1].min(), end_coords[1].min()), max(start_coords[1].max(), end_coords[1].max())

x_grid = np.linspace(x_min, x_max, 1000)  # 500 grid points for longitude
y_grid = np.linspace(y_min, y_max, 1000)  # 500 grid points for latitude
X, Y = np.meshgrid(x_grid, y_grid)       # Create 2D grid
grid_coords = np.vstack([X.ravel(), Y.ravel()])  # Flatten grid for KDE evaluation

# KDE for start points
kde_start = gaussian_kde(start_coords,bw_method=0.03)(grid_coords).reshape(X.shape)  # Reshape to 2D grid

# KDE for end points
kde_end = gaussian_kde(end_coords,bw_method=0.03)(grid_coords).reshape(X.shape)  # Reshape to 2D grid

# Normalize KDE values for heatmap intensity (0 to 1)
kde_start_norm = (kde_start - kde_start.min()) / (kde_start.max() - kde_start.min())
kde_end_norm = (kde_end - kde_end.min()) / (kde_end.max() - kde_end.min())

# Step 4: Visualize KDE on Folium Maps
def add_kde_to_map(kde_values, x_grid, y_grid, map_obj):
    """Overlay KDE results as heatmap on a Folium map."""
    for i in range(len(x_grid) - 1):
        for j in range(len(y_grid) - 1):
            intensity = kde_values[j, i]
            if intensity > 0:  # Only add cells with positive intensity
                folium.Rectangle(
                    bounds=[[y_grid[j], x_grid[i]], [y_grid[j + 1], x_grid[i + 1]]],
                    color=None,
                    fill=True,
                    fill_color=f'rgba(255, 0, 0, {intensity})',  # Red heatmap color
                    fill_opacity=intensity,  # Transparency based on intensity
                ).add_to(map_obj)

# Create the map for start points
m_start = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="CartoDB positron")
add_kde_to_map(kde_start_norm, x_grid, y_grid, m_start)

# Add metro station markers
for station in metro_stations:
    coordinates = station['coordinates']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [lon, lat]
        radius=2,
        color='purple',
        fill=True,
        fill_opacity=0.9,
    ).add_to(m_start)

# Save the start point map
m_start.save("shanghai_bike_start_kde.html")

# Create the map for end points
m_end = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="CartoDB positron")
add_kde_to_map(kde_end_norm, x_grid, y_grid, m_end)

# Add metro station markers
for station in metro_stations:
    coordinates = station['coordinates']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],
        radius=2,
        color='purple',
        fill=True,
        fill_opacity=0.9,
    ).add_to(m_end)

# Save the end point map
m_end.save("shanghai_bike_end_kde.html")

# Print completion message
print("Maps with KDE heatmaps have been saved:")
print("- Start point map: shanghai_bike_start_kde.html")
print("- End point map: shanghai_bike_end_kde.html")