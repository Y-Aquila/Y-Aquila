import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

# Fichiers nécessaires
CELL_SCORES_FILE = "cell_scores.geojson"  # Fichier des scores des cellules
FLOOD_FILE = "merged_event_data.geojson"        # Fichier des inondations
RESIDENTIAL_FILE = "merged_obj_data.geojson"  # Fichier des zones résidentielles
AOI_DIR = "DATA/filtered_data_aoi_only"              # Répertoire des AOI

def visualize_cell_importance_with_aoi_dir(cell_scores_file, flood_file, residential_file, aoi_dir):
    # Charger les données
    print("Chargement des données...")
    cell_scores_gdf = gpd.read_file(cell_scores_file)
    flood_gdf = gpd.read_file(flood_file)
    residential_gdf = gpd.read_file(residential_file)

    # Charger et fusionner les AOI
    print("Chargement des AOI...")
    aoi_gdfs = []
    for file_name in os.listdir(aoi_dir):
        if file_name.endswith(".geojson"):
            file_path = os.path.join(aoi_dir, file_name)
            gdf = gpd.read_file(file_path)
            aoi_gdfs.append(gdf)
    aoi_gdf = gpd.GeoDataFrame(pd.concat(aoi_gdfs, ignore_index=True), crs=gdf.crs)

    # Création de la figure
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Tracer les cellules avec un dégradé basé sur le score (jaune à rouge)
    cell_scores_gdf.plot(
        ax=ax,
        column="score",  # Colonne contenant les scores des cellules
        cmap="YlOrRd",                 # Palette de couleurs jaune -> rouge
        legend=True,
        alpha=0.8,
        edgecolor="black",
        linewidth=0.2,
        legend_kwds={"label": "Cell importance score"}
    )

    # Tracer les zones d'inondation en bleu transparent
    flood_gdf.plot(
        ax=ax,
        color="blue",
        alpha=0.3,  # Transparence pour éviter de cacher les autres couches
    )

    # Tracer les zones résidentielles en vert
    residential_gdf.plot(
        ax=ax,
        color="green",
        alpha=0.4,
    )

    # Tracer les contours des AOI
    aoi_gdf.boundary.plot(
        ax=ax,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )


    # Ajouter des titres et légendes
    ax.set_title("Visualization of cells with their importance scores", fontsize=16)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Afficher la figure
    plt.tight_layout()
    plt.show()

# Appel de la fonction
visualize_cell_importance_with_aoi_dir(CELL_SCORES_FILE, FLOOD_FILE, RESIDENTIAL_FILE, AOI_DIR)
