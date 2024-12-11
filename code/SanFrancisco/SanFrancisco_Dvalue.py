import folium
from scipy.stats import gaussian_kde
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

# Step 1: Load GeoJSON data for metro stations
geojson_path = 'data/SanFrancisco/SanFrancisco_railwaystation.geojson' 
with open(geojson_path, 'r', encoding='utf-8') as f:
    metro_data = json.load(f)

# Extract metro station coordinates
metro_stations = []
for feature in metro_data['features']:
    coordinates = feature['geometry']['coordinates']
    name = feature['properties'].get('name', 'Metro Station')
    metro_stations.append({'name': name, 'coordinates': coordinates})

# Step 2: Load bike-sharing data
file_path = 'data/SanFrancisco/202008-baywheels-tripdata.csv' 

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
start_coords = np.vstack([filtered_data["start_lng"], filtered_data["start_lat"]])  # [lng, lat]
end_coords = np.vstack([filtered_data["end_lng"], filtered_data["end_lat"]])     # [lng, lat]

# Define function to calculate distance
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# Calculate distances for each trip
distances = haversine_distance(filtered_data["start_lat"], filtered_data["start_lng"],
                               filtered_data["end_lat"], filtered_data["end_lng"])

# Add distances to DataFrame
filtered_data["distance_km"] = distances

# Define function to check if a point is within 150 meters of a station
def is_within_150m(lat1, lon1, lat2, lon2):
    return haversine_distance(lat1, lon1, lat2, lon2) <= 0.15

# Calculate distances for trips near each metro station
results = []

for station in metro_stations:
    station_name = station['name']
    station_lat, station_lng = station['coordinates'][1], station['coordinates'][0]
    
    # Filter trips that start or end within 150 meters of the station
    nearby_trips = filtered_data[
        filtered_data.apply(lambda row: is_within_150m(row["start_lat"], row["start_lng"], station_lat, station_lng) or
                                      is_within_150m(row["end_lat"], row["end_lng"], station_lat, station_lng), axis=1)
    ]
    
    # Calculate average distance and 90th percentile distance for these trips
    avg_distance = nearby_trips["distance_km"].mean()
    percentile_90_distance = nearby_trips["distance_km"].mean() * 0.9
    
    # Append results
    results.append({
        'station_name': station_name,
        'average_distance': avg_distance,
        'percentile_90_distance': percentile_90_distance
    })

# Print results
for result in results:
    print(f"Station: {result['station_name']}")
    print(f"Average Distance: {result['average_distance']} km")
    print(f"90th Percentile Distance: {result['percentile_90_distance']} km")
    print()

# Plot 90th percentile distances as a bar chart
station_names = [result['station_name'] for result in results]
percentile_90_distances = [result['percentile_90_distance'] for result in results]

plt.figure(figsize=(12, 6))
plt.barh(station_names, percentile_90_distances, color='skyblue')
plt.xlabel('90th Percentile Distance (km)')
plt.title('90th Percentile Distance for Each Metro Station')
plt.tight_layout()
plt.show()
