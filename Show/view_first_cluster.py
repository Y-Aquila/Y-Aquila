import os
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd

def sort_clusters_by_importance(G, clusters):
    """
    Trie les clusters par importance (somme des scores des nœuds).
    """
    cluster_scores = []
    for cluster in clusters:
        importance = sum(G.nodes[node]['score'] for node in cluster)
        cluster_scores.append((cluster, importance))
    
    # Trier par importance croissante
    sorted_clusters = sorted(cluster_scores, key=lambda x: x[1])
    return [cluster for cluster, _ in sorted_clusters]

def plot_clusters_with_priority(G, clusters, output_file="cluster_priority_visualization.png"):
    """
    Affiche les clusters par ordre de priorité avec une palette 'coolwarm'.
    Parameters:
        G: NetworkX graph avec 'position'.
        clusters: Liste des clusters triés par importance.
        output_file: Nom du fichier PNG à sauvegarder.
    """
    clusters = [clusters[len(clusters)-1]]
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
    fig, ax = plt.subplots(figsize=(15, 15))

    flood_gdf.plot(ax=ax, color='blue', alpha=0.5, label='Flood Zones')
    building_gdf.plot(ax=ax, color='green', alpha=0.5, label='Buildings')

    # Tracer les contours des AOI
    aoi_gdf.boundary.plot(
        ax=ax,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )

    # Palette de couleurs 'coolwarm'
    cmap = plt.cm.coolwarm
    norm = plt.Normalize(0, len(clusters) - 1)  # Normaliser en fonction du nombre de clusters

    # Tracer les clusters avec leurs couleurs
    for i, cluster in enumerate(clusters):
        cluster_coords = [G.nodes[node]['position'] for node in cluster]

        # Couleur basée sur le rang du cluster
        color = "red"

        # Afficher les nœuds du cluster
        ax.scatter(
            [coord[1] for coord in cluster_coords],
            [coord[0] for coord in cluster_coords],
            color=color
        )

    # Ajouter légende et titre
    plt.title("Clusters by Priority", fontsize=18)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, label="Cluster Priority")
    plt.savefig(output_file, dpi=300)
    print(f"Visualisation sauvegardée dans {output_file}")
    plt.show()

# Charger le graphe et les clusters
graph_path = "OptimizePath/drone_graph.json"
clusters_file = "OptimizePath/clusters.json"

with open(graph_path, "r") as f:
    graph_data = json.load(f)
with open(clusters_file, "r") as f:
    clusters = json.load(f)

G = nx.node_link_graph(graph_data)

# Trier les clusters par importance
sorted_clusters = sort_clusters_by_importance(G, [set(cluster) for cluster in clusters])

# Afficher les clusters avec priorité
plot_clusters_with_priority(G, sorted_clusters)
