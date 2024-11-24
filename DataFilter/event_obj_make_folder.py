import geopandas as gpd

# Fichiers d'entrée et de sortie
RESIDENTIAL_FILE = "merged_obj_data.geojson"  # Fichier des bâtiments résidentiels
FLOOD_FILE = "merged_event_data.geojson"  # Fichier des inondations
OUTPUT_INTERSECTION_FILE = "event_obj_intersection.geojson"  # Fichier de sortie GeoJSON

def save_building_flood_intersection(residential_file, flood_file, output_file):
    # Charger les fichiers d'entrée
    print("Chargement des données...")
    residential_gdf = gpd.read_file(residential_file).to_crs("EPSG:32633")
    flood_gdf = gpd.read_file(flood_file).to_crs(residential_gdf.crs)

    # Calculer l'intersection entre les bâtiments et les zones inondées
    print("Calcul de l'intersection bâtiments/inondations...")
    building_flood_intersection = gpd.overlay(residential_gdf, flood_gdf, how="intersection", keep_geom_type=True)

    # Ajouter une colonne pour l'aire des intersections
    building_flood_intersection["intersect_area"] = building_flood_intersection.geometry.area

    # Sauvegarder les résultats dans un fichier GeoJSON
    print(f"Enregistrement des résultats dans {output_file}...")
    building_flood_intersection.to_file(output_file, driver="GeoJSON")
    print("Fichier enregistré avec succès.")

# Appel de la fonction
save_building_flood_intersection(RESIDENTIAL_FILE, FLOOD_FILE, OUTPUT_INTERSECTION_FILE)
