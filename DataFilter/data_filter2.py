import os
import shutil


SOURCE_DIR = "DATA/filtered_data"
DEST_DIR = "DATA/filtered_data_2"

def filter_aoi_with_del(source_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)

    # Step 1 : Find the AOIs with DEL folders
    aoi_with_del = set()
    for file_name in os.listdir(source_dir):
        if "DEL" in file_name and "AOI" in file_name:
            aoi_id = next((part for part in file_name.split("_") if part.startswith("AOI")), None)
            if aoi_id:
                aoi_with_del.add(aoi_id)

    print(f"AOI ayant des DEL : {sorted(aoi_with_del)}")

    # Step 2 : Copy the folders
    for file_name in os.listdir(source_dir):
        # Vérifier si le fichier appartient à une AOI avec DEL
        if any(aoi_id in file_name for aoi_id in aoi_with_del):
            src_path = os.path.join(source_dir, file_name)
            dest_path = os.path.join(dest_dir, file_name)
            shutil.copy(src_path, dest_path)
            print(f"Copié : {file_name}")

    print(f"Filtrage terminé. Fichiers copiés dans : {dest_dir}")

filter_aoi_with_del(SOURCE_DIR, DEST_DIR)
