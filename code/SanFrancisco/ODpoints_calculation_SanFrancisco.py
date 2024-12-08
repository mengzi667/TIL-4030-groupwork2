import pandas as pd
import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

# SanFrancisco data
# Load CSV file (shared bike data)
mobike_data = pd.read_csv('C:/Users/syl20/Desktop/Research and Design Methods/Research Code/SanFrancisco/202008-baywheels-tripdata.csv')
# Load GeoJSON file (metro station data)
metro_stations = gpd.read_file('C:/Users/syl20/Desktop/Research and Design Methods/Research Code/SanFrancisco/SanFrancisco_railwaystation.geojson')

# Extract start and end coordinates of shared bikes
mobike_od = mobike_data[['start_lng', 'start_lat', 'end_lat', 'end_lng']]
mobike_od.dropna(inplace=True)

# Extract longitude and latitude of metro stations
metro_stations['lon'] = metro_stations.geometry.x
metro_stations['lat'] = metro_stations.geometry.y
metro_station_coords = metro_stations[['lon', 'lat']].values

# Combine start and end points of shared bikes into a single array
od_coords = np.vstack([mobike_od[['start_lng', 'start_lat']].values,
                       mobike_od[['end_lat', 'end_lng']].values])

# Build a k-d tree for shared bike OD points to optimize spatial queries
od_tree = cKDTree(od_coords)

# Define distance bands (e.g., 100-200m, 200-300m)
distance_thresholds = np.arange(100, 1600, 100)  # From 100m to 1500m with 100m intervals

# Initialize a dictionary to store results for each metro station and distance band
results_per_station = {}

# Iterate over each metro station and compute OD density for each distance band
for idx, station in enumerate(metro_station_coords):
    station_results = {}
    previous_threshold_degrees = 0  # Start with the innermost radius
    
    for threshold in distance_thresholds:
        # Convert threshold to degrees (1 degree ≈ 111 km)
        threshold_degrees = threshold / 1000 / 111
        
        # Query k-d tree for points within the current threshold
        points_within_threshold = set(od_tree.query_ball_point(station, threshold_degrees))
        
        # Query k-d tree for points within the previous threshold
        points_within_previous_threshold = set(od_tree.query_ball_point(station, previous_threshold_degrees))
        
        # Calculate points within the distance band by subtracting sets
        points_in_band = points_within_threshold - points_within_previous_threshold
        
        # Calculate the area of the ring (distance band) in square kilometers
        area_outer = np.pi * (threshold / 1000) ** 2
        area_inner = np.pi * ((threshold - 100) / 1000) ** 2
        band_area = area_outer - area_inner  # Area in square kilometers
        
        # Calculate density (points per square kilometer)
        density = len(points_in_band) / band_area if band_area > 0 else 0
        
        # Store the density for the current distance band
        station_results[f"{threshold-100}-{threshold}m"] = density
        
        # Update the previous threshold
        previous_threshold_degrees = threshold_degrees
    
    # Save results for this station
    results_per_station[f'Station_{idx+1}'] = station_results

# Convert results to a Pandas DataFrame for better readability
density_results = pd.DataFrame(results_per_station).T

# Save the results to a CSV file
density_results.to_csv('C:/Users/syl20/Desktop/Research and Design Methods/Research Code/SanFrancisco/metro_station_density_by_distance_band.csv', index_label="Station")

# Print the final results
print(density_results)

# Step 1: Summarize density or count for all stations at each distance band
density_results_df = pd.DataFrame(results_per_station).T

# Calculate the total density for each distance band
total_density_per_band = density_results_df.sum(axis=0)

# Calculate the average density for each distance band
average_density_per_band = density_results_df.mean(axis=0)

# Step 2: Calculate weighted average density for each distance band
weighted_density_per_band = []

for idx, threshold in enumerate(distance_thresholds):
    weighted_density_sum = 0
    total_area = 0

    for station, densities in results_per_station.items():
        # Get the density and calculate the area for the current band
        density = densities[f"{threshold-100}-{threshold}m"]
        area_outer = np.pi * (threshold / 1000) ** 2  # Outer radius area
        area_inner = np.pi * ((threshold - 100) / 1000) ** 2  # Inner radius area
        band_area = area_outer - area_inner  # Area in km²

        # Add to weighted sum and total area
        weighted_density_sum += density * band_area
        total_area += band_area

    # Calculate weighted average density for this band
    weighted_avg_density = weighted_density_sum / total_area if total_area > 0 else 0
    weighted_density_per_band.append(weighted_avg_density)

# Step 3: Plot the results
distance_labels = [f"{threshold-100}-{threshold}m" for threshold in distance_thresholds]

# Plot total density
plt.figure(figsize=(10, 6))
plt.bar(range(len(distance_labels)), weighted_density_per_band, alpha=0.5, label="Weighted Avg Density", color="skyblue")
plt.plot(range(len(distance_labels)), weighted_density_per_band, marker="o", label="Trend", color="blue")

# Customize the plot
plt.xticks(range(len(distance_labels)), distance_labels, rotation=45)
plt.xlabel("Distance (m)")
plt.ylabel("Weighted Avg Density (OD points per square kilometer)")
plt.title("Weighted Average Density by Distance Band")
plt.legend()
plt.tight_layout()

plt.savefig('C:/Users/syl20/Desktop/Research and Design Methods/Research Code/SanFrancisco/SanFrancisco_OD_density_distance.png', dpi=300)

# Show the plot
plt.show()

