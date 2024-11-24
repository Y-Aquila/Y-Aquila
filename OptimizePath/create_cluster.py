import networkx as nx
import json

def calculate_clusters_with_fusion_no_propagation(G, score_threshold, distance_max):
    """
    Calculate clusters from a graph based on a score threshold and a maximum distance.
    Nodes with scores below the threshold are ignored, and clusters are merged if they overlap.

    """
    clusters = []  # List to store clusters
    visited = set()  # Set to track nodes that have already been assigned to a cluster

    for node, data in G.nodes(data=True):
        # Skip nodes that do not meet the score threshold or are already visited
        if data['score'] < score_threshold:
            continue

        # Initialize a new cluster with the current node as the center
        cluster = {node}

        # Add neighbors within the specified maximum distance
        for neighbor, edge_data in G[node].items():
            if edge_data.get("weight", float("inf")) <= distance_max:
                cluster.add(neighbor)

        # Merge the new cluster with existing clusters if they overlap
        merged = False
        for existing_cluster in clusters:
            if cluster & existing_cluster:  # Check for non-empty intersection
                existing_cluster.update(cluster)
                merged = True
                break

        # If no merging occurred, add the new cluster to the list
        if not merged:
            clusters.append(cluster)

        # Mark all nodes in the cluster as visited
        visited.update(cluster)

    return clusters

def save_clusters_to_file(clusters, output_file):
    """
    Save clusters to a JSON file.

    Parameters:
        clusters (List[set]): The clusters to save.
        output_file (str): Path to the output JSON file.
    """
    # Convert clusters to a list of lists for JSON serialization
    clusters_list = [list(cluster) for cluster in clusters]

    # Save to the specified file
    with open(output_file, "w") as f:
        json.dump(clusters_list, f, indent=4)
    print(f"Clusters saved to {output_file}")

# Load the graph from a JSON file
graph_path = "OptimizePath/drone_graph.json"
with open(graph_path, "r") as f:
    graph_data = json.load(f)

# Convert the JSON data back to a NetworkX graph
G = nx.node_link_graph(graph_data)

# Compute clusters with a score threshold and maximum distance
score_threshold = 0.2  # Minimum score to be a cluster center
distance_max = 3000  # Maximum distance between the center and its neighbors
clusters = calculate_clusters_with_fusion_no_propagation(G, score_threshold, distance_max)

# Save the clusters to a JSON file
output_file = "OptimizePath/clusters.json"
save_clusters_to_file(clusters, output_file)
