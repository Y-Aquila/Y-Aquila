import os
import shutil


FILTERED_DATA_DIR = "DATA/filtered_data_2"
FILTERED_DATA_DEL_DIR = "DATA/filtered_data_del"


os.makedirs(FILTERED_DATA_DEL_DIR, exist_ok=True)

# Filter the DEL folders
for root, dirs, files in os.walk(FILTERED_DATA_DIR):
    for file in files:
        if "DEL" in file and file.endswith(".geojson"):
            src_path = os.path.join(root, file)
            dst_path = os.path.join(FILTERED_DATA_DEL_DIR, file)
            shutil.copy2(src_path, dst_path)
            print(f"Folder copied : {file}")

print(f"Task over.")
