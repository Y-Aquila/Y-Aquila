import os
import zipfile
import geopandas as gpd


DATA_DIR = "DATA/copernicus_data"
EXTRACT_DIR = "DATA/copernicus_extracted"
FILTERED_DIR = "DATA/filtered_data"

os.makedirs(EXTRACT_DIR, exist_ok=True)
os.makedirs(FILTERED_DIR, exist_ok=True)

def extract_zip_files(data_dir, extract_dir):

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".zip"):
                zip_path = os.path.join(root, file)
                print(f"Decompression of : {zip_path}")
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(extract_dir, os.path.splitext(file)[0]))
                        print(f"Folders extract to : {os.path.join(extract_dir, os.path.splitext(file)[0])}")
                except Exception as e:
                    print(f"Error during the decompression of {zip_path} : {e}")

def analyze_and_filter_shapefiles(data_dir, filtered_dir):

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".shp") or file.endswith(".geojson"):
                file_path = os.path.join(root, file)
                print(f"Analyse et filtrage du fichier : {file_path}")
                try:
                    # Download the geospatial folder
                    gdf = gpd.read_file(file_path)
                    print(f"Nombre de features : {len(gdf)}")
                    print("Colonnes disponibles :", gdf.columns)

                    # Columns to conserv
                    relevant_columns = ["geometry", "event_type", "area", "obj_type", "damage_pref"]
                    gdf = gdf[[col for col in relevant_columns if col in gdf.columns]]

                    # Download the filtered data
                    output_path = os.path.join(filtered_dir, f"filtered_{file}.geojson")
                    gdf.to_file(output_path, driver="GeoJSON")
                    print(f"Fichier filtré sauvegardé sous : {output_path}")
                except Exception as e:
                    print(f"Erreur lors de l'analyse/filtrage du fichier {file_path} : {e}")

# Step 1: Decompresse the ZIP folders
extract_zip_files(DATA_DIR, EXTRACT_DIR)

# Step 2 : Filter the folders
analyze_and_filter_shapefiles(EXTRACT_DIR, FILTERED_DIR)
