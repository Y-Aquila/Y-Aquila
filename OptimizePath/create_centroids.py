import geopandas as gpd


input_path = "cell_scores.geojson"  
output_path = "OptimizePath/cell_scores_centroid.geojson"


gdf = gpd.read_file(input_path)

# Centroids calcul
gdf['geometry'] = gdf.geometry.centroid

gdf.to_file(output_path, driver="GeoJSON")

