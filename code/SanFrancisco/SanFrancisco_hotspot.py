import folium
from folium.plugins import HeatMap
import pandas as pd
import json

# Step 1: Load metro station data from GeoJSON
geojson_path = 'TIL-4030-groupwork2/data/SanFrancisco/SanFrancisco_railwaystation.geojson' 
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

# Extract metro station coordinates and names
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load bike-sharing data
file_path = 'TIL-4030-groupwork2/data/SanFrancisco/202008-baywheels-tripdata.csv' 
bike_data = pd.read_csv(file_path)

# Step 3: Filter data within the bounding box
lng_min, lng_max = -122.5233, -122.3551
lat_min, lat_max = 37.7083, 37.8163

filtered_data = bike_data[
    (bike_data["start_lng"] >= lng_min) & (bike_data["start_lng"] <= lng_max) &
    (bike_data["start_lat"] >= lat_min) & (bike_data["start_lat"] <= lat_max) &
    (bike_data["end_lng"] >= lng_min) & (bike_data["end_lng"] <= lng_max) &
    (bike_data["end_lat"] >= lat_min) & (bike_data["end_lat"] <= lat_max)
]

# Extract start and end coordinates
start_coords = filtered_data[["start_lat", "start_lng"]].values.tolist()
end_coords = filtered_data[["end_lat", "end_lng"]].values.tolist()

# Step 4: Create two interactive maps
# Map for start points
m_start = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="OpenStreetMap")

# Add heatmap for start points
HeatMap(
    data=start_coords,
    max_zoom=16,
    radius=15,
).add_to(m_start)

# Add metro station markers (as CircleMarker) to the start point map
for station in metro_stations:
    coordinates = station['coordinates']
    name = station['name']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [longitude, latitude]
        radius=5,  # Circle radius
        color='purple',
        fill=True,
        fill_color='purple',
        fill_opacity=0.8,
        popup=name
    ).add_to(m_start)

# Save start point heatmap
m_start.save("sf_bike_start_heatmap.html")

# Map for end points
m_end = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="OpenStreetMap")

# Add heatmap for end points
HeatMap(
    data=end_coords,
    max_zoom=16,
    radius=15,
).add_to(m_end)

# Add metro station markers (as CircleMarker) to the end point map
for station in metro_stations:
    coordinates = station['coordinates']
    name = station['name']
    folium.CircleMarker(
        location=[coordinates[1], coordinates[0]],  # GeoJSON uses [longitude, latitude]
        radius=5,  # Circle radius
        color='purple',
        fill=True,
        fill_color='purple',
        fill_opacity=0.8,
        popup=name
    ).add_to(m_end)

# Save end point heatmap
m_end.save("sf_bike_end_heatmap.html")

print("The heatmaps for start and end points have been saved as HTML files:")
print("- Start point heatmap: sf_bike_start_heatmap.html")
print("- End point heatmap: sf_bike_end_heatmap.html")