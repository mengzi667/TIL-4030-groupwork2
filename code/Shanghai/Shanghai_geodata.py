import geopandas as gpd
from shapely.geometry import box

# 1. 加载 GeoJSON 文件
railway_geojson_file = 'data/Shanghai/Shanghai_railwaystation.geojson'
crossroad_geojson_file = 'data/Shanghai/crossroad.geojson'
road_geojson_file = 'data/Shanghai/road.geojson'
shop_geojson_file = 'data/Shanghai/shop.geojson'
landuse_geojson_file = 'data/Shanghai/landuse.geojson'

railway_gdf = gpd.read_file(railway_geojson_file)
crossroad_gdf = gpd.read_file(crossroad_geojson_file)
road_gdf = gpd.read_file(road_geojson_file)
shop_gdf = gpd.read_file(shop_geojson_file)
landuse_gdf = gpd.read_file(landuse_geojson_file)

# 确保 GeoDataFrame 有有效的投影
for gdf in [railway_gdf, crossroad_gdf, road_gdf, shop_gdf]:
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)  # 假设你的数据是 WGS84 坐标系
    gdf.to_crs(epsg=3857, inplace=True)  # 转换为以米为单位的投影坐标系

# 2. 获取边界并创建网格
def create_grid(gdf, cell_size=1000):
    """
    创建网格，网格的大小为 cell_size（单位：米）
    """
    bounds = gdf.total_bounds  # 获取区域边界 [minx, miny, maxx, maxy]
    xmin, ymin, xmax, ymax = bounds
    grid_cells = []
    x = xmin
    while x < xmax:
        y = ymin
        while y < ymax:
            grid_cells.append(box(x, y, x + cell_size, y + cell_size))
            y += cell_size
        x += cell_size
    grid = gpd.GeoDataFrame({"geometry": grid_cells}, crs=gdf.crs)
    return grid

grid = create_grid(railway_gdf)

# # 3. 统计每个网格中的地理信息数量
# # def count_geometries_in_grid(grid, gdf, label_column):
# #     """
# #     统计每个网格中包含的地理对象数量
# #     """
# #     labels = gdf[label_column].unique()
# #     for label in labels:
# #         grid[label] = grid.geometry.apply(
# #             lambda cell: gdf[(gdf[label_column] == label) & (gdf.intersects(cell))].shape[0]
# #         )
# #     return grid

# # 统计每个网格中的路口数量
# grid['crossroad_count'] = grid.geometry.apply(
#     lambda cell: crossroad_gdf[crossroad_gdf.intersects(cell)].shape[0]
# )

# # 统计每个网格中的道路长度
# grid['road_length'] = grid.geometry.apply(
#     lambda cell: road_gdf[road_gdf.intersects(cell)].length.sum()
# )

# # 统计每个网格中的商业设施数量
# grid['shop_count'] = grid.geometry.apply(
#     lambda cell: shop_gdf[shop_gdf.intersects(cell)].shape[0]
# )

# # 统计每个网格中的用地类型面积
# landuse_types = landuse_gdf['landuse'].unique()
# for landuse_type in landuse_types:
#     grid[f'{landuse_type}_area'] = grid.geometry.apply(
#         lambda cell: landuse_gdf[(landuse_gdf['landuse'] == landuse_type) & (landuse_gdf.intersects(cell))].intersection(cell).area.sum()
#     )

# # 4. 将结果转换回地理坐标系 (WGS84) 以便保存为 CSV 文件
# grid = grid.to_crs(epsg=4326)

# # 5. 保存结果为新的 CSV 文件
# grid.to_csv('data/Shanghai/grid_with_counts.csv', index=False)

# print("Grid with counts saved to 'data/Shanghai/grid_with_counts.csv'")

import pandas as pd

# # 加载 landuse GeoJSON 文件
# landuse_geojson_file = 'data/Shanghai/landuse.geojson'
# landuse_gdf = gpd.read_file(landuse_geojson_file)

# # 确保 landuse GeoDataFrame 有有效的投影
# if landuse_gdf.crs is None:
#     landuse_gdf.set_crs(epsg=4326, inplace=True)  # 假设你的数据是 WGS84 坐标系
# landuse_gdf.to_crs(epsg=3857, inplace=True)  # 转换为以米为单位的投影坐标系

# # 统计每个网格中 landuse 里不同 landuse 种类的面积之和
# landuse_types = landuse_gdf['landuse'].unique()
# for landuse_type in landuse_types:
#     grid[f'{landuse_type}_area'] = grid.geometry.apply(
#         lambda cell: landuse_gdf[(landuse_gdf['landuse'] == landuse_type) & (landuse_gdf.intersects(cell))].intersection(cell).area.sum()
#     )

# # 统计每个网格内的铁路车站数量
# grid['railway_station_count'] = grid.geometry.apply(
#     lambda cell: railway_gdf[railway_gdf.intersects(cell)].shape[0]
# )

# # 将结果转换回地理坐标系 (WGS84) 以便保存为 CSV 文件
# grid = grid.to_crs(epsg=4326)
# grid.to_csv('data/Shanghai/grid_with_counts_railwaystation.csv', index=False)
# print("Grid with railwaystation areas saved to 'data/Shanghai/grid_with_counts_railwaystation.csv'")


# # 读取现有的 CSV 文件
# existing_grid_df = pd.read_csv('data/Shanghai/grid_with_counts.csv')

# # 确保现有的 DataFrame 和新的 DataFrame 有相同的索引
# existing_grid_df.index = grid.index

# # 合并新的 landuse 数据
# grid_df = pd.DataFrame(grid.drop(columns='geometry'))
# merged_df = pd.concat([existing_grid_df, grid_df], axis=1)

# # 保存结果为新的 CSV 文件
# merged_df.to_csv('data/Shanghai/grid_with_counts.csv', index=False)

# print("Updated grid with railwaystation areas saved to 'data/Shanghai/grid_with_counts.csv'")

# 加载 bicycle lane 和 bus GeoJSON 文件
bicyclelane_geojson_file = 'data/Shanghai/bicyclelane.geojson'
bus_geojson_file = 'data/Shanghai/bus.geojson'

bicyclelane_gdf = gpd.read_file(bicyclelane_geojson_file)
bus_gdf = gpd.read_file(bus_geojson_file)

# 确保 GeoDataFrame 有有效的投影
for gdf in [bicyclelane_gdf, bus_gdf]:
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)  # 假设你的数据是 WGS84 坐标系
    gdf.to_crs(epsg=3857, inplace=True)  # 转换为以米为单位的投影坐标系

# 统计每个网格内的自行车道长度
grid['bicycle_lane_length'] = grid.geometry.apply(
    lambda cell: bicyclelane_gdf[bicyclelane_gdf.intersects(cell)].length.sum()
)

# 统计每个网格内的公交车站数量
grid['bus_station_count'] = grid.geometry.apply(
    lambda cell: bus_gdf[bus_gdf.intersects(cell)].shape[0]
)

# 将结果转换回地理坐标系 (WGS84) 以便保存为 CSV 文件
grid = grid.to_crs(epsg=4326)
grid.to_csv('data/Shanghai/grid_with_counts_bicyclelane_busstation.csv', index=False)
print("Grid with bicycle lane lengths and bus station counts saved to 'data/Shanghai/grid_with_counts_bicyclelane_busstation.csv'")

# 读取现有的 CSV 文件
existing_grid_df = pd.read_csv('data/Shanghai/grid_with_counts.csv')

# 确保现有的 DataFrame 和新的 DataFrame 有相同的索引
existing_grid_df.index = grid.index

# 合并新的 bicycle lane 和 bus station 数据
bicycle_lane_bus_station_df = grid[['bicycle_lane_length', 'bus_station_count']]
merged_df = pd.concat([existing_grid_df, bicycle_lane_bus_station_df], axis=1)

# 保存结果为新的 CSV 文件
merged_df.to_csv('data/Shanghai/grid_with_counts.csv', index=False)

print("Updated grid with bicycle lane lengths and bus station counts saved to 'data/Shanghai/grid_with_counts.csv'")