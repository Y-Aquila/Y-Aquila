import os
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import pandas as pd

def sort_clusters_by_importance(G, clusters):

    cluster_scores = []
    for cluster in clusters:
        importance = sum(G.nodes[node]['score'] for node in cluster)
        cluster_scores.append((cluster, importance))
    
    # Trier par importance décroissante
    sorted_clusters = sorted(cluster_scores, key=lambda x: x[1], reverse=True)
    return [cluster for cluster, _ in sorted_clusters]

def find_tour_in_cluster_with_priority(G, cluster):


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

def plot_clusters_with_paths(G, clusters, tours, output_file="cluster_visualization.png"):


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
    aoi_gdf.plot(ax=ax, color='black', alpha=0.2, label='AOIs')
    flood_gdf.plot(ax=ax, color='blue', alpha=0.5, label='Flood Zones')
    building_gdf.plot(ax=ax, color='green', alpha=0.5, label='Buildings')

    # Tracer les clusters avec leurs parcours
    colors = plt.cm.get_cmap("tab20", len(clusters))
    for i, cluster in enumerate(clusters):
        tour = tours[f"Cluster_{i + 1}"]
        cluster_coords = [G.nodes[node]['position'] for node in cluster]

        # Afficher les nœuds du cluster
        ax.scatter(
            [coord[1] for coord in cluster_coords],
            [coord[0] for coord in cluster_coords],
            label=f"Cluster {i + 1}", s=50, color=colors(i)
        )

        # Tracer le parcours
        tour_coords = [G.nodes[node]['position'] for node in tour]
        ax.plot(
            [coord[1] for coord in tour_coords],
            [coord[0] for coord in tour_coords],
            linestyle='-', color=colors(i), linewidth=2
        )

        # Ajouter des annotations avec l'ordre de parcours
        for order, node in enumerate(tour, start=1):
            coord = G.nodes[node]['position']
            ax.text(
                coord[1], coord[0], str(order),
                fontsize=8, ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )

    # Ajouter légende et titre
    plt.title("Clusters et Parcours Dynamiques", fontsize=18)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
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

# Trier les clusters et calculer les parcours
sorted_clusters = sort_clusters_by_importance(G, [set(cluster) for cluster in clusters])
cluster_tours = {}
for i, cluster in enumerate(sorted_clusters):
    print(f"Calcul du parcours pour le cluster {i + 1}...")
    tour = find_tour_in_cluster_with_priority(G, cluster)
    cluster_tours[f"Cluster_{i + 1}"] = tour

# Afficher les clusters et les parcours
plot_clusters_with_paths(G, sorted_clusters, cluster_tours)
