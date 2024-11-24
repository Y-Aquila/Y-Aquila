import os
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import json

def plot_clusters_from_file(G, clusters_file, output_file="OptimizePath/clusters_dynamic_all_nodes.png"):
    """
    Affiche les clusters sur une carte statique à partir d'un fichier JSON.
    Parameters:
        G: NetworkX graph avec 'position'.
        clusters_file: Fichier JSON contenant les clusters.
        output_file: Nom du fichier PNG à sauvegarder.
    """
    # Charger les clusters depuis le fichier JSON
    print("Chargement des clusters depuis le fichier...")
    with open(clusters_file, "r") as f:
        clusters = json.load(f)

    # Charger les couches géographiques
    aoi_dir = "DATA/filtered_data_aoi_only"
    aoi_files = [os.path.join(aoi_dir, file) for file in os.listdir(aoi_dir) if file.endswith('.geojson')]
    aoi_gdfs = [gpd.read_file(file) for file in aoi_files]
    aoi_gdf = gpd.GeoDataFrame(pd.concat(aoi_gdfs, ignore_index=True))

    flood_path = "merged_event_data.geojson"
    building_path = "merged_obj_data.geojson"
    flood_gdf = gpd.read_file(flood_path)
    building_gdf = gpd.read_file(building_path)

    # Créer la carte
    fig, ax = plt.subplots(figsize=(12, 12))

    flood_gdf.plot(ax=ax, color='blue', alpha=0.5, label='Flood Zones')
    building_gdf.plot(ax=ax, color='green', alpha=0.5, label='Buildings')

    # Tracer les contours des AOI
    aoi_gdf.boundary.plot(
        ax=ax,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )

    # Assigner des couleurs aux clusters
    colors = plt.cm.get_cmap("tab20", len(clusters))
    for i, cluster in enumerate(clusters):
        cluster_coords = [G.nodes[node]['position'] for node in cluster]
        ax.scatter(
            [coord[1] for coord in cluster_coords],  # Longitude
            [coord[0] for coord in cluster_coords],  # Latitude
            label=f"Cluster {i+1}", s=20, color=colors(i)
        )

    plt.title("Disaster Clusters")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.savefig(output_file, dpi=300)
    print(f"Carte des clusters sauvegardée dans {output_file}")
    plt.show()


# Charger le graphe
graph_path = "OptimizePath/drone_graph.json"
clusters_file = "OptimizePath/clusters.json"

with open(graph_path, "r") as f:
    graph_data = json.load(f)

G = nx.node_link_graph(graph_data)

# Afficher les clusters sur la carte
plot_clusters_from_file(G, clusters_file)
