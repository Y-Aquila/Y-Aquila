import os
import geopandas as gpd
import shutil

INPUT_DIR = "DATA/filtered_data_2"
OUTPUT_DIR = "DATA/filtered_data_3"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def filter_geojson_files(input_dir, output_dir):

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(input_dir, file_name)
            print(f"Processing of : {file_name}")
            try:
                # Download the GeoJSON folder
                gdf = gpd.read_file(file_path)

                # Check if the folder contains the necessary columns
                if not gdf.empty and ("event_type" in gdf.columns or "obj_type" in gdf.columns):
                    # Filter the lignes with event_type or "11-Residential Buildings"
                    if (
                        "event_type" in gdf.columns and not gdf[gdf["event_type"].notnull()].empty
                    ) or (
                        "obj_type" in gdf.columns and "11-Residential Buildings" in gdf["obj_type"].values
                    ):
                        # Copy the folder in the exit folder
                        shutil.copy(file_path, os.path.join(output_dir, file_name))
                        print(f"Copy : {file_name}")
                    else:
                        print(f"No relevant lines found in : {file_name}")
                else:
                    print(f"Necessary columns missing or empty folder: {file_name}")

            except Exception as e:
                print(f"Erreur lors du traitement de {file_name}: {e}")


filter_geojson_files(INPUT_DIR, OUTPUT_DIR)

print(f"The filtered files have been copied to  : {OUTPUT_DIR}")
