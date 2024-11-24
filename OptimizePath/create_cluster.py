import networkx as nx
import json

def calculate_clusters_with_fusion_no_propagation(G, score_threshold, distance_max):


    clusters = []  # Liste des clusters
    visited = set()  # Ensemble des nœuds déjà inclus dans un cluster

    for node, data in G.nodes(data=True):
        # Ignorer les nœuds en dessous du seuil ou déjà assignés
        if data['score'] < score_threshold:
            continue

        # Initialiser un nouveau cluster avec le nœud central
        cluster = {node}

        # Ajouter les voisins respectant la distance
        for neighbor, edge_data in G[node].items():
            if (
                edge_data.get("weight", float("inf")) <= distance_max
            ):
                cluster.add(neighbor)

        # Fusionner avec les clusters existants qui partagent des cellules
        merged = False
        for existing_cluster in clusters:
            if cluster & existing_cluster:  # Intersection non vide
                existing_cluster.update(cluster)
                merged = True
                break

        # Ajouter comme un nouveau cluster s'il n'y a pas eu de fusion
        if not merged:
            clusters.append(cluster)

        # Marquer tous les nœuds du cluster comme visités
        visited.update(cluster)

    return clusters

def save_clusters_to_file(clusters, output_file):

    # Convertir les clusters en liste de listes pour JSON
    clusters_list = [list(cluster) for cluster in clusters]

    # Sauvegarder dans un fichier JSON
    with open(output_file, "w") as f:
        json.dump(clusters_list, f, indent=4)
    print(f"Clusters sauvegardés dans {output_file}")

# Charger le graphe depuis le fichier JSON
graph_path = "OptimizePath/drone_graph.json"
with open(graph_path, "r") as f:
    graph_data = json.load(f)

G = nx.node_link_graph(graph_data)

# Calculer les clusters avec un seuil de score et une distance maximale
score_threshold = 0.2  # Seuil de score pour être un centre de cluster
distance_max = 3000  # Distance maximale entre le centre et ses voisins
clusters = calculate_clusters_with_fusion_no_propagation(G, score_threshold, distance_max)

# Sauvegarder les clusters
output_file = "OptimizePath/clusters.json"
save_clusters_to_file(clusters, output_file)
