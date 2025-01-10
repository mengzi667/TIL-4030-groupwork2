import folium
from folium.plugins import HeatMap
import pandas as pd
import json
import numpy as np

# Step 1: Load metro station data from GeoJSON
geojson_path = 'data/Shanghai/Shanghai_railwaystation.geojson'
with open(geojson_path, 'r') as f:
    metro_data = json.load(f)

metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load bike-sharing data
file_path = 'data/Shanghai/mobike_shanghai_sample_updated.csv'
bike_data = pd.read_csv(file_path)

# Extract start and end coordinates
start_coords = bike_data[["start_location_y", "start_location_x"]].values.tolist()
end_coords = bike_data[["end_location_y", "end_location_x"]].values.tolist()

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

# Step 3: Create two maps
m_start = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="OpenStreetMap")
HeatMap(
    data=start_coords,
    max_zoom=16,
    radius=20,  # radius is in pixels
    useGeoUnit=True,
    gradient=None  # Default gradient
).add_to(m_start)

for station in metro_stations:
    folium.CircleMarker(
        location=[station['coordinates'][1], station['coordinates'][0]],
        radius=4,
        color='blue',
        fill=True,
        fill_color='blue',
        popup=station['name'],
    ).add_to(m_start)

m_start.get_root().html.add_child(folium.Element(start_legend_html))
m_start.save("shanghai_bike_start_heatmap.html")

m_end = folium.Map(location=[31.23, 121.47], zoom_start=11, tiles="OpenStreetMap")
HeatMap(
    data=end_coords,
    max_zoom=16,
    radius=20,
).add_to(m_end)

for station in metro_stations:
    folium.CircleMarker(
        location=[station['coordinates'][1], station['coordinates'][0]],
        radius=4,
        color='blue',
        fill=True,
        fill_color='blue',
        popup=station['name'],
    ).add_to(m_end)

m_end.get_root().html.add_child(folium.Element(end_legend_html))
m_end.save("shanghai_bike_end_heatmap.html")

print("The heatmaps for start and end points have been saved:")
print("- shanghai_bike_start_heatmap.html")
print("- shanghai_bike_end_heatmap.html")