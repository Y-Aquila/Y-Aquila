import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Dossiers contenant les fichiers
AOI_DATA_DIR = "DATA/filtered_data_aoi_only"
FLOOD_FILE = "merged_event_data.geojson"        # Fichier des inondations
RESIDENTIAL_FILE = "merged_obj_data.geojson"  # Fichier des zones résidentielles

def display_polygons_with_aoi(event_file, aoi_dir, obj_file):
    """
    Affiche tous les polygones (event_type) et superpose les contours des AOI.
    """

    # Charger les fichiers GeoJSON
    flood_gdf = gpd.read_file(event_file)
    residential_gdf = gpd.read_file(obj_file)

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
    
    # Tracer les zones d'inondation
    flood_layer = flood_gdf.plot(
        ax=ax,
        color="blue",
        alpha=0.4
    )

    # Tracer les zones résidentielles
    residential_layer = residential_gdf.plot(
        ax=ax,
        color="green",
        alpha=0.4
    )

    # Tracer les contours des AOI
    aoi_layer = aoi_gdf.boundary.plot(
        ax=ax,
        color="black",
        linestyle="--",
        linewidth=0.8
    )

    # Ajouter une légende manuelle
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="blue", lw=4, alpha=0.4, label="Flooded areas"),
        Line2D([0], [0], color="green", lw=4, alpha=0.4, label="Residential areas"),
        Line2D([0], [0], color="black", lw=1.5, linestyle="--", label="AOIs")
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    # Mise en forme
    ax.set_title("Floods in Valencia")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.show()

# Exécuter la fonction
display_polygons_with_aoi(FLOOD_FILE, AOI_DATA_DIR, RESIDENTIAL_FILE)
