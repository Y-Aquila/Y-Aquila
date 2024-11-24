import os
import geopandas as gpd


INPUT_DIR = "DATA/filtered_data_3"  
OUTPUT_DIR_OBJ = "DATA/filtered_obj_data"  

def filter_obj_type(input_dir, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(input_dir, file_name)
            try:

                gdf = gpd.read_file(file_path)

                # Check if the folder contains a column 'obj_type'
                if "obj_type" in gdf.columns:
                    # Filter on "11-Residential Buildings"
                    filtered_gdf = gdf[gdf["obj_type"] == "11-Residential Buildings"]
                    
                    if not filtered_gdf.empty:
                        # Save the filtered folder
                        output_path = os.path.join(output_dir, file_name)
                        filtered_gdf.to_file(output_path, driver="GeoJSON")
                        print(f"Filtered Folder save : {output_path}")
            except Exception as e:
                print(f"Error during the processing of {file_name}: {e}")

filter_obj_type(INPUT_DIR, OUTPUT_DIR_OBJ)
