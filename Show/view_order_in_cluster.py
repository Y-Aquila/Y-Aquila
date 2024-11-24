import os
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import pandas as pd

def plot_first_cluster_with_numbers(G, first_cluster, tour, output_file="first_cluster_visualization.png"):

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

    # Fond statique
    flood_gdf.plot(ax=ax, color='blue', alpha=0.5)
    building_gdf.plot(ax=ax, color='green', alpha=0.5)

    # Tracer les contours des AOI
    aoi_gdf.boundary.plot(
        ax=ax,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )

    # Afficher les nœuds du premier cluster
    cluster_coords = [G.nodes[node]['position'] for node in first_cluster]
    ax.scatter(
        [coord[1] for coord in cluster_coords],
        [coord[0] for coord in cluster_coords],
        s=50, color="red"
    )

    # Ajouter des annotations avec l'ordre de parcours
    for order, node in enumerate(tour, start=1):
        coord = G.nodes[node]['position']
        ax.text(
            coord[1], coord[0], str(order),
            fontsize=4, ha='center', va='center',  # Taille des numéros encore plus petite
        )

    # Titre et axes
    plt.title("First Cluster with Path Numbers", fontsize=18)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
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

# Trier les clusters
def sort_clusters_by_importance(G, clusters):
    """
    Trie les clusters par importance (somme des scores des nœuds).
    """
    cluster_scores = []
    for cluster in clusters:
        importance = sum(G.nodes[node]['score'] for node in cluster)
        cluster_scores.append((cluster, importance))
    
    # Trier par importance décroissante
    sorted_clusters = sorted(cluster_scores, key=lambda x: x[1], reverse=True)
    return [cluster for cluster, _ in sorted_clusters]

sorted_clusters = sort_clusters_by_importance(G, [set(cluster) for cluster in clusters])

# Calculer le parcours pour le premier cluster uniquement
first_cluster = sorted_clusters[0]  # Le cluster le plus important

def find_tour_in_cluster_with_priority(G, cluster):
    """
    Calcule le parcours dans un cluster, basé sur le score et la distance.
    """
    from networkx.algorithms.approximation import traveling_salesman_problem as tsp

    # Trier les nœuds par score décroissant
    cluster_nodes = [(node, G.nodes[node]['score']) for node in cluster]
    cluster_nodes.sort(key=lambda x: x[1], reverse=True)

    # Chemin basé sur les scores
    tour = [node for node, score in cluster_nodes if score > 0]

    # Ajouter les nœuds restants en minimisant la distance
    remaining_nodes = {node for node, score in cluster_nodes if score == 0}
    if remaining_nodes:
        subgraph = G.subgraph(remaining_nodes)
        distance_tour = tsp(subgraph, weight="weight")
        tour.extend(distance_tour)

    # Retourner au point de départ
    if tour and tour[0] != tour[-1]:
        tour.append(tour[0])

    return tour

first_cluster_tour = find_tour_in_cluster_with_priority(G, first_cluster)

# Afficher le premier cluster avec les numéros de parcours
plot_first_cluster_with_numbers(G, first_cluster, first_cluster_tour)
