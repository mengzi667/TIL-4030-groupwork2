import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely import wkt

# Load bike-sharing data
bike_data = pd.read_csv('data/SanFrancisco/202008-baywheels-tripdata.csv')

# Load grid data
grid_data = pd.read_csv('data/SanFrancisco/grid_with_counts.csv')

# Convert the geometry column of the grid data to Shapely Polygon objects
grid_data['geometry'] = grid_data['geometry'].apply(wkt.loads)
grid_gdf = gpd.GeoDataFrame(grid_data, geometry='geometry', crs="EPSG:4326")

# Convert the start and end points of the bike data to Shapely Point objects
bike_data['start_point'] = bike_data.apply(lambda row: Point(row['start_lng'], row['start_lat']), axis=1)
bike_data['end_point'] = bike_data.apply(lambda row: Point(row['end_lng'], row['end_lat']), axis=1)

# Convert to GeoDataFrame
bike_start_gdf = gpd.GeoDataFrame(bike_data, geometry='start_point', crs="EPSG:4326")
bike_end_gdf = gpd.GeoDataFrame(bike_data, geometry='end_point', crs="EPSG:4326")

# Count the number of start points within each grid
start_join = gpd.sjoin(grid_gdf, bike_start_gdf, how='left', predicate='contains')
start_counts = start_join.groupby(start_join.index).size()

# Count the number of end points within each grid
end_join = gpd.sjoin(grid_gdf, bike_end_gdf, how='left', predicate='contains')
end_counts = end_join.groupby(end_join.index).size()

# Add the results to the grid data
grid_gdf['start_count'] = grid_gdf.index.map(start_counts).fillna(0).astype(int)
grid_gdf['end_count'] = grid_gdf.index.map(end_counts).fillna(0).astype(int)

# Drop rows where all columns except 'geometry', 'start_count', and 'end_count' are zero
cols_to_check = grid_gdf.columns.difference(['geometry', 'start_count', 'end_count'])
grid_gdf = grid_gdf[~(grid_gdf[cols_to_check] == 0).all(axis=1).values]

# Save as a new CSV file
output_path = 'data/SanFrancisco/grid_with_bike_counts.csv'
grid_gdf.to_csv(output_path, index=False)

print(f"Results have been saved to: {output_path}")
