import networkx as nx
from geopy.distance import geodesic
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

def calculate_clusters_dynamic_all_nodes(G, score_threshold, distance_max):

    clusters = [
        {node} for node, data in G.nodes(data=True) if data['score'] >= score_threshold
    ]

    merged = True
    while merged:
        merged = False
        new_clusters = []
        while clusters:
            current_cluster = clusters.pop(0)
            nodes_to_add = set()
            for node in current_cluster:
                for other_node in G.nodes:
                    if other_node not in current_cluster:
                        distance = geodesic(
                            G.nodes[node]['position'], G.nodes[other_node]['position']
                        ).meters
                        if distance <= distance_max:
                            nodes_to_add.add(other_node)

            current_cluster.update(nodes_to_add)
            for other_cluster in clusters[:]:
                if current_cluster & other_cluster:
                    current_cluster.update(other_cluster)
                    clusters.remove(other_cluster)
                    merged = True

            new_clusters.append(current_cluster)
        clusters = new_clusters

    return clusters

def evaluate_clusters(G, threshold, distance_max):
    """
    Évalue les clusters pour un seuil et une distance donnés.
    """
    clusters = calculate_clusters_dynamic_all_nodes(G, score_threshold=threshold, distance_max=distance_max)

    num_clusters = len(clusters)
    cluster_sizes = [len(cluster) for cluster in clusters]
    avg_cluster_size = sum(cluster_sizes) / num_clusters if num_clusters > 0 else 0

    geo_sizes = []
    for cluster in clusters:
        positions = [G.nodes[node]["position"] for node in cluster]
        if len(positions) > 1:
            distances = [
                geodesic(positions[i], positions[j]).meters
                for i in range(len(positions)) for j in range(i + 1, len(positions))
            ]
            geo_sizes.append(max(distances) if distances else 0)
    avg_geo_size = sum(geo_sizes) / len(geo_sizes) if geo_sizes else 0

    return {
        "num_clusters": num_clusters,
        "avg_cluster_size": avg_cluster_size,
        "avg_geo_size": avg_geo_size
    }

def optimize_parameters(G, threshold_range, distance_range):
    """
    Optimise les paramètres pour un graphe donné.
    """
    results = []
    for threshold in threshold_range:
        for distance in distance_range:
            metrics = evaluate_clusters(G, threshold, distance)
            results.append({
                "threshold": threshold,
                "distance_max": distance,
                **metrics
            })

    results_df = pd.DataFrame(results)

    # Critères de sélection
    optimal_results = results_df[
        (results_df["num_clusters"] >= 10) &
        (results_df["num_clusters"] <= 50) &
        (results_df["avg_geo_size"] <= 2000)
    ]
    best_config = optimal_results.sort_values(by="avg_geo_size").iloc[0] if not optimal_results.empty else None

    return results_df, best_config

def visualize_results(results_df, distance_values):
    """
    Visualise les résultats sous forme de graphique.
    """
    plt.figure(figsize=(10, 6))
    for distance in distance_values:
        subset = results_df[results_df["distance_max"] == distance]
        plt.plot(subset["threshold"], subset["num_clusters"], label=f"Distance {distance} m")
    plt.xlabel("Threshold")
    plt.ylabel("Number of Clusters")
    plt.title("Number of Clusters vs Threshold for Different Distances")
    plt.legend()
    plt.show()

# Charger le graphe
graph_path = "OptimizePath/drone_graph.json"
with open(graph_path, "r") as f:
     graph_data = json.load(f)

G = nx.node_link_graph(graph_data)

# Optimisation des paramètres
threshold_range = np.linspace(0.3, 0.8, 6)  # De 0.3 à 0.8 par pas de 0.1
distance_range = np.arange(500, 3000, 500)  # De 500 à 2500 m par pas de 500

results_df, best_config = optimize_parameters(G, threshold_range, distance_range)

# Affichage des résultats
print("Résultats complets :\n", results_df)
if best_config is not None:
    print("\nMeilleure configuration :\n", best_config)

# Visualisation
visualize_results(results_df, distance_range)
