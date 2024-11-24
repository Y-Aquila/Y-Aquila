import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os

# Fichiers d'entrée
GRID_FILE = "global_filtered_grid.geojson"  # Grille
FLOOD_FILE = "merged_event_data.geojson"  # Inondations
RESIDENTIAL_FILE = "merged_obj_data.geojson"  # Bâtiments résidentiels
AOI_DIR = "DATA/filtered_data_aoi_only"    

def calculate_and_visualize_intersection(grid_file, flood_file, residential_file,aoi_dir):
    # Charger les données
    print("Chargement des données...")
    grid_gdf = gpd.read_file(grid_file).to_crs("EPSG:32633")
    flood_gdf = gpd.read_file(flood_file).to_crs(grid_gdf.crs)
    residential_gdf = gpd.read_file(residential_file).to_crs(grid_gdf.crs)

    # Calculer l'intersection bâtiments/inondations
    print("Calcul de l'intersection bâtiments/inondations...")
    building_flood_intersection = gpd.read_file("event_obj_intersection.geojson")

    # Charger et fusionner les AOI
    print("Chargement des AOI...")
    aoi_gdfs = []
    for file_name in os.listdir(aoi_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(aoi_dir, file_name)
            gdf = gpd.read_file(file_path)
            aoi_gdfs.append(gdf)
    aoi_gdf = gpd.GeoDataFrame(pd.concat(aoi_gdfs, ignore_index=True), crs=gdf.crs)

    # Vérification des données calculées
    print("Exemple de bâtiment inondé :")
    print(building_flood_intersection.head())

    # Création de la figure
    fig, ax = plt.subplots(figsize=(12, 12))

    grid_gdf = grid_gdf.to_crs("EPSG:4326")
    flood_gdf = flood_gdf.to_crs(grid_gdf.crs)
    residential_gdf = residential_gdf.to_crs(grid_gdf.crs)
    building_flood_intersection = building_flood_intersection.to_crs(grid_gdf.crs)
    
    # Tracer les inondations
    print("Affichage des inondations...")
    flood_gdf.plot(ax=ax, color='blue', alpha=0.5)

    # Tracer les bâtiments résidentiels
    print("Affichage des bâtiments résidentiels...")
    residential_gdf.plot(ax=ax, color='green', alpha=0.5)

    # Tracer l'intersection entre les bâtiments et les inondations
    print("Affichage de l'intersection...")
    building_flood_intersection.plot(ax=ax, color='red', alpha=0.7)

    # Tracer les contours des AOI
    aoi_gdf.boundary.plot(
        ax=ax,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )

    # Tracer la grille pour le contexte
    print("Affichage de la grille...")
    grid_gdf.boundary.plot(ax=ax, color='black', linewidth=0.5, alpha=0.5)

    # Ajouter une légende et des titres
    plt.legend(loc="upper right")
    plt.title("Flooded inhabited areas")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # Afficher la carte
    plt.tight_layout()
    plt.show()

# Appel de la fonction
calculate_and_visualize_intersection(GRID_FILE, FLOOD_FILE, RESIDENTIAL_FILE,AOI_DIR)
