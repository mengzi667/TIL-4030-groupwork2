import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 加载共享单车数据
bike_data_path = "data/SanFrancisco/202008-baywheels-tripdata.csv"  # 替换为实际路径
bike_data = pd.read_csv(bike_data_path)

# 加载地铁站数据
subway_data_path = "data/SanFrancisco/SanFrancisco_railwaystation.geojson"  # 替换为实际路径
subway_data = gpd.read_file(subway_data_path)

# 将地铁站数据从地理坐标系 (EPSG:4326) 转换为投影坐标系 (UTM)
subway_data = subway_data.to_crs(epsg=3857)  # 使用 Web Mercator 投影（适合大部分城市）

# 为地铁站创建150米和1公里缓冲区
subway_data['buffer_150m'] = subway_data.geometry.buffer(150)  # 150米缓冲区
subway_data['buffer_1km'] = subway_data.geometry.buffer(1000)  # 1公里缓冲区

# 将共享单车起点和终点转换为 GeoDataFrame
start_points = gpd.GeoDataFrame(
    bike_data,
    geometry=gpd.points_from_xy(bike_data['start_lng'], bike_data['start_lat']),
    crs="EPSG:4326"
).to_crs(epsg=3857)  # 转换为投影坐标系

end_points = gpd.GeoDataFrame(
    bike_data,
    geometry=gpd.points_from_xy(bike_data['end_lng'], bike_data['end_lat']),
    crs="EPSG:4326"
).to_crs(epsg=3857)  # 转换为投影坐标系

# 筛选地铁站1公里范围内的共享单车（起点和终点）
start_in_1km = start_points[start_points.geometry.within(subway_data.unary_union.buffer(1000))]
end_in_1km = end_points[end_points.geometry.within(subway_data.unary_union.buffer(1000))]

# 筛选地铁站150米范围内的共享单车（起点和终点）
start_in_150m = start_points[start_points.geometry.within(subway_data.unary_union.buffer(150))]
end_in_150m = end_points[end_points.geometry.within(subway_data.unary_union.buffer(150))]

# 计算数量
total_in_1km = len(start_in_1km) + len(end_in_1km)
total_in_150m = len(start_in_150m) + len(end_in_150m)

# 计算比例
proportion = total_in_150m / total_in_1km * 100

print(f"地铁站150米范围内的共享单车数量: {total_in_150m}")
print(f"地铁站1公里范围内的共享单车总数量: {total_in_1km}")
print(f"比例: {proportion:.2f}%")
