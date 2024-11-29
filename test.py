import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Load the CSV file into a DataFrame
df = pd.read_csv('202410-baywheels-tripdata.csv')

# Display the first few rows of the DataFrame
df.head()

# Plot the start coordinates
plt.figure(figsize=(10, 6))
plt.scatter(df['start_lng'], df['start_lat'], c='blue', label='Start', alpha=0.5, s=1)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Start Locations of Rides')
plt.legend()
plt.show()

# Plot the end coordinates
plt.figure(figsize=(10, 6))
plt.scatter(df['end_lng'], df['end_lat'], c='red', label='End', alpha=0.5, s=1)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('End Locations of Rides')
plt.legend()
plt.show()
# Remove rows with NaN values in the relevant columns
df_clean = df.dropna(subset=['start_lat', 'start_lng', 'end_lat', 'end_lng'])

# Calculate the center of the map
map_center = [df_clean['start_lat'].mean(), df_clean['start_lng'].mean()]

import plotly.express as px

# Plot start locations on a map
fig_start = px.scatter_mapbox(df_clean, lat='start_lat', lon='start_lng', color_discrete_sequence=['blue'], 
                              title='Start Locations of Rides', zoom=10, height=600)
fig_start.update_layout(mapbox_style="open-street-map", mapbox_zoom=10, mapbox_center={"lat": map_center[0], "lon": map_center[1]})
fig_start.show()

# Plot end locations on a map
fig_end = px.scatter_mapbox(df_clean, lat='end_lat', lon='end_lng', color_discrete_sequence=['red'], 
                            title='End Locations of Rides', zoom=10, height=600)
fig_end.update_layout(mapbox_style="open-street-map", mapbox_zoom=10, mapbox_center={"lat": map_center[0], "lon": map_center[1]})
fig_end.show()


# Prepare data for clustering
start_coords = df_clean[['start_lat', 'start_lng']]
end_coords = df_clean[['end_lat', 'end_lng']]

# Function to calculate WCSS for a range of cluster numbers
def calculate_wcss(data):
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, random_state=0)
        kmeans.fit(data)
        wcss.append(kmeans.inertia_)
    return wcss

# Calculate WCSS for start and end coordinates
wcss_start = calculate_wcss(start_coords)
wcss_end = calculate_wcss(end_coords)

# Plot the WCSS to find the optimal number of clusters
plt.figure(figsize=(10, 6))
plt.plot(range(1, 11), wcss_start, marker='o', label='Start Locations')
plt.plot(range(1, 11), wcss_end, marker='o', label='End Locations')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.title('Elbow Method For Optimal Number of Clusters')
plt.legend()
plt.show()

# Determine the optimal number of clusters (for example, let's assume it's 3)
optimal_clusters = 3

# Apply k-means clustering with the optimal number of clusters
kmeans_start = KMeans(n_clusters=optimal_clusters, random_state=0).fit(start_coords)
kmeans_end = KMeans(n_clusters=optimal_clusters, random_state=0).fit(end_coords)

# Add cluster labels to the DataFrame
df_clean['start_cluster'] = kmeans_start.labels_
df_clean['end_cluster'] = kmeans_end.labels_

# Extract cluster centers
start_cluster_centers = kmeans_start.cluster_centers_
end_cluster_centers = kmeans_end.cluster_centers_

print("Start Cluster Centers:")
print(start_cluster_centers)

print("End Cluster Centers:")
print(end_cluster_centers)

# Calculate SSE (Sum of Squared Errors)
sse_start = kmeans_start.inertia_
sse_end = kmeans_end.inertia_

print(f"SSE for start locations: {sse_start}")
print(f"SSE for end locations: {sse_end}")

# Plot start locations with cluster centers
plt.figure(figsize=(10, 6))
plt.scatter(df_clean['start_lng'], df_clean['start_lat'], c=df_clean['start_cluster'], cmap='viridis', alpha=0.5, s=1)
plt.scatter(start_cluster_centers[:, 1], start_cluster_centers[:, 0], c='red', marker='X', s=100, label='Cluster Centers')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Start Locations of Rides with Cluster Centers')
plt.legend()
plt.show()

# Plot end locations with cluster centers
plt.figure(figsize=(10, 6))
plt.scatter(df_clean['end_lng'], df_clean['end_lat'], c=df_clean['end_cluster'], cmap='viridis', alpha=0.5, s=1)
plt.scatter(end_cluster_centers[:, 1], end_cluster_centers[:, 0], c='red', marker='X', s=100, label='Cluster Centers')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('End Locations of Rides with Cluster Centers')
plt.legend()
plt.show()