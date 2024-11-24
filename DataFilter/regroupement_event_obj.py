import os
import geopandas as gpd
import pandas as pd

# Répertoires
EVENT_DIR = "DATA/filtered_event_data"  
RESIDENTIAL_DIR = "DATA/filtered_obj_data" 
OUTPUT_EVENT_FILE = "merged_event_data.geojson"  
OUTPUT_RESIDENTIAL_FILE = "merged_obj_data.geojson"  


PROJECTED_CRS = "EPSG:32633"

def prepare_flood_and_residential(flood_dir, residential_dir, output_flood_file, output_residential_file):

    print("Event processing...")
    flood_gdfs = []
    for file_name in os.listdir(flood_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(flood_dir, file_name)
            flood_gdf = gpd.read_file(file_path)
            flood_gdfs.append(flood_gdf.to_crs(PROJECTED_CRS))  
    flood_gdf = gpd.GeoDataFrame(pd.concat(flood_gdfs, ignore_index=True), crs=PROJECTED_CRS)

    flood_gdf = flood_gdf.to_crs("EPSG:4326")

    flood_gdf.to_file(output_flood_file, driver="GeoJSON")

    print("Residential Buildings processing...")
    residential_gdfs = []
    for file_name in os.listdir(residential_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(residential_dir, file_name)
            res_gdf = gpd.read_file(file_path)
            if "obj_type" in res_gdf.columns:
                res_gdf = res_gdf[(res_gdf["obj_type"] == "11-Residential Buildings") &
                                  (res_gdf.geometry.type.isin(["Polygon", "MultiPolygon"]))]
            residential_gdfs.append(res_gdf.to_crs(PROJECTED_CRS)) 
    residential_gdf = gpd.GeoDataFrame(pd.concat(residential_gdfs, ignore_index=True), crs=PROJECTED_CRS)

    residential_gdf = residential_gdf.to_crs("EPSG:4326")

    residential_gdf.to_file(output_residential_file, driver="GeoJSON")

prepare_flood_and_residential(EVENT_DIR, RESIDENTIAL_DIR, OUTPUT_EVENT_FILE, OUTPUT_RESIDENTIAL_FILE)
