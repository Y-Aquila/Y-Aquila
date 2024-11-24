import os
import shutil


FILTERED_DATA_DEL_DIR = "DATA/filtered_data_del"
AOI_ONLY_DIR = "DATA/filtered_data_aoi_only"

os.makedirs(AOI_ONLY_DIR, exist_ok=True)

# Browse folders and select the folders with "areaOfInterest" in their name.
for file_name in os.listdir(FILTERED_DATA_DEL_DIR):
    if "areaOfInterest" in file_name:
        source_path = os.path.join(FILTERED_DATA_DEL_DIR, file_name)
        destination_path = os.path.join(AOI_ONLY_DIR, file_name)
        shutil.copy(source_path, destination_path)
        print(f"Folder copied : {file_name}")

print(f"Task over.")
