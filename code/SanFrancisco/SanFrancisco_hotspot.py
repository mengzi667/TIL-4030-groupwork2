import folium
from folium.plugins import HeatMap
import pandas as pd
import json

# Step 1: Load metro station data from GeoJSON
geojson_path = 'data/SanFrancisco/SanFrancisco_railwaystation.geojson'
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

# Extract metro station coordinates and names
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load bike-sharing data
file_path = 'data/SanFrancisco/202008-baywheels-tripdata.csv'
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

# Dynamic classification legend for start points
start_legend_html = f'''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 150px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; padding: 10px;">
    <b>Legend (Start Density)</b><br>
    <div style="background: linear-gradient(to right, #00ff00, #ffff00, #ff0000); height: 18px; margin-bottom: 8px;"></div>
    <span style="float: left;">0</span>
    <span style="float: right;">1</span>
    <br style="clear: both;">
    <i style="border: 2px solid blue; width: 12px; height: 12px; border-radius: 50%; float: left; margin-right: 8px;"></i> Metro Station<br>
</div>
'''

# Dynamic classification legend for end points
end_legend_html = f'''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 150px; height: 120px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; padding: 10px;">
    <b>Legend (End Density)</b><br>
    <div style="background: linear-gradient(to right, #00ff00, #ffff00, #ff0000); height: 18px; margin-bottom: 8px;"></div>
    <span style="float: left;">0</span>
    <span style="float: right;">1</span>
    <br style="clear: both;">
    <i style="border: 2px solid blue; width: 12px; height: 12px; border-radius: 50%; float: left; margin-right: 8px;"></i> Metro Station<br>
</div>
'''

# Step 4: Create two maps
m_start = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="OpenStreetMap")
HeatMap(
    data=start_coords,
    max_zoom=16,
    radius=15,
).add_to(m_start)

for station in metro_stations:
    folium.CircleMarker(
        location=[station['coordinates'][1], station['coordinates'][0]],
        radius=5,
        color='blue',
        fill=True,
        fill_color='blue',
        popup=station['name'],
    ).add_to(m_start)

m_start.get_root().html.add_child(folium.Element(start_legend_html))
m_start.save("sf_bike_start_heatmap.html")

m_end = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="OpenStreetMap")
HeatMap(
    data=end_coords,
    max_zoom=16,
    radius=15,
).add_to(m_end)

for station in metro_stations:
    folium.CircleMarker(
        location=[station['coordinates'][1], station['coordinates'][0]],
        radius=5,
        color='blue',
        fill=True,
        fill_color='blue',
        popup=station['name'],
    ).add_to(m_end)

m_end.get_root().html.add_child(folium.Element(end_legend_html))
m_end.save("sf_bike_end_heatmap.html")

print("The heatmaps for start and end points have been saved:")
print("- sf_bike_start_heatmap.html")
print("- sf_bike_end_heatmap.html")
