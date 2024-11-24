import os
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon


INPUT_DIR = "DATA/filtered_data_3"  
OUTPUT_DIR_EVENT = "DATA/filtered_event_data"  

def filter_event_types_and_polygons(input_dir, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(input_dir, file_name)
            try:
                gdf = gpd.read_file(file_path)


                if "event_type" in gdf.columns:
                    # Filter the lignes with event_types and exploitable geometries
                    filtered_gdf = gdf[
                        (~gdf["event_type"].isna()) &
                        (gdf["geometry"].apply(lambda geom: isinstance(geom, (Polygon, MultiPolygon))))
                    ]

                    if not filtered_gdf.empty:
                        # Save the filtered folder
                        output_path = os.path.join(output_dir, file_name)
                        filtered_gdf.to_file(output_path, driver="GeoJSON")
                        print(f"Filtered folder save : {output_path}")

            except Exception as e:
                print(f"Error during the processing of {file_name}: {e}")


filter_event_types_and_polygons(INPUT_DIR, OUTPUT_DIR_EVENT)
