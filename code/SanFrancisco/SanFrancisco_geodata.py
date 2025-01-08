import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt

# 1. 加载 GeoJSON 文件
geojson_file = 'data/SanFrancisco/SanFrancisco_railwaystation.geojson'  # 替换为你的 GeoJSON 文件路径
gdf = gpd.read_file(geojson_file)

# 确保 GeoDataFrame 有有效的投影
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)  # 假设你的数据是 WGS84 坐标系
gdf = gdf.to_crs(epsg=3857)  # 转换为以米为单位的投影坐标系

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

grid = create_grid(gdf)

# 3. 统计每个网格中的地理信息数量
def count_geometries_in_grid(grid, gdf):
    """
    统计每个网格中包含的地理对象数量
    """
    grid["feature_count"] = grid.geometry.apply(
        lambda cell: gdf[gdf.intersects(cell)].shape[0]
    )
    return grid

grid_with_counts = count_geometries_in_grid(grid, gdf)

# 4. 将结果转换回地理坐标系 (WGS84) 以便可视化
grid_with_counts = grid_with_counts.to_crs(epsg=4326)

# 5. 可视化结果
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
grid_with_counts.plot(column="feature_count", ax=ax, legend=True, cmap="OrRd", alpha=0.6)
plt.title("Number of Geographic Features per 1km Zone")
plt.show()

# # 6. 保存结果为新的 GeoJSON 文件
# grid_with_counts.to_file("grid_with_counts.geojson", driver="GeoJSON")


# 6. 保存结果为新的 CSV 文件
grid_with_counts[['geometry', 'feature_count']].to_csv('data/SanFrancisco/grid_with_counts.csv', index=False)

print("Grid with counts saved to 'data/SanFrancisco/grid_with_counts.csv'")