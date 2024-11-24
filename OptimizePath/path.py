import os
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import pandas as pd

def sort_clusters_by_importance(G, clusters):

    cluster_scores = []
    for cluster in clusters:
        # Calculate total importance of a cluster
        importance = sum(G.nodes[node]['score'] for node in cluster)
        cluster_scores.append((cluster, importance))
    
    # Sort clusters by importance in descending order
    sorted_clusters = sorted(cluster_scores, key=lambda x: x[1], reverse=True)
    return [cluster for cluster, _ in sorted_clusters]

def find_tour_in_cluster_with_priority(G, cluster):
    """
    Find a tour within a cluster, prioritizing nodes by their scores and minimizing distances.

    Parameters:
        G (networkx.Graph): The graph containing the nodes and edges.
        cluster (set): A cluster of node IDs.

    Returns:
        List[int]: An ordered list of node IDs representing the tour.
    """
    from networkx.algorithms.approximation import traveling_salesman_problem as tsp

    # Sort nodes in the cluster by score in descending order
    cluster_nodes = [(node, G.nodes[node]['score']) for node in cluster]
    cluster_nodes.sort(key=lambda x: x[1], reverse=True)

    # Start the tour with nodes that have a score > 0
    tour = [node for node, score in cluster_nodes if score > 0]

    # Add remaining nodes to the tour by minimizing distance
    remaining_nodes = {node for node, score in cluster_nodes if score == 0}
    if remaining_nodes:
        subgraph = G.subgraph(remaining_nodes)
        distance_tour = tsp(subgraph, weight="weight")
        tour.extend(distance_tour)

    # Return to the starting point if the tour is not closed
    if tour and tour[0] != tour[-1]:
        tour.append(tour[0])

    return tour

def plot_clusters_with_paths(G, clusters, tours, output_file="cluster_visualization.png"):
    """
    Plot clusters with their dynamic paths on a geographic map.

    Parameters:
        G (networkx.Graph): The graph containing nodes with positions.
        clusters (List[set]): List of clusters to plot.
        tours (dict): Dictionary of tours for each cluster.
        output_file (str): Path to save the visualization image.
    """
    # Load geographic layers for AOI, flood zones, and buildings
    aoi_dir = "DATA/filtered_data_aoi_only"
    aoi_files = [os.path.join(aoi_dir, file) for file in os.listdir(aoi_dir) if file.endswith('.geojson')]
    aoi_gdfs = [gpd.read_file(file) for file in aoi_files]
    aoi_gdf = gpd.GeoDataFrame(pd.concat(aoi_gdfs, ignore_index=True))

    flood_path = "merged_event_data.geojson"
    building_path = "merged_obj_data.geojson"
    flood_gdf = gpd.read_file(flood_path)
    building_gdf = gpd.read_file(building_path)

    # Create the map
    fig, ax = plt.subplots(figsize=(15, 15))

    # Plot static background layers
    aoi_gdf.plot(ax=ax, color='black', alpha=0.2, label='AOIs')
    flood_gdf.plot(ax=ax, color='blue', alpha=0.5, label='Flood Zones')
    building_gdf.plot(ax=ax, color='green', alpha=0.5, label='Buildings')

    # Plot each cluster with its path
    colors = plt.cm.get_cmap("tab20", len(clusters))
    for i, cluster in enumerate(clusters):
        tour = tours[f"Cluster_{i + 1}"]
        cluster_coords = [G.nodes[node]['position'] for node in cluster]

        # Plot cluster nodes
        ax.scatter(
            [coord[1] for coord in cluster_coords],
            [coord[0] for coord in cluster_coords],
            label=f"Cluster {i + 1}", s=50, color=colors(i)
        )

        # Plot the tour path
        tour_coords = [G.nodes[node]['position'] for node in tour]
        ax.plot(
            [coord[1] for coord in tour_coords],
            [coord[0] for coord in tour_coords],
            linestyle='-', color=colors(i), linewidth=2
        )

        # Add annotations with tour order
        for order, node in enumerate(tour, start=1):
            coord = G.nodes[node]['position']
            ax.text(
                coord[1], coord[0], str(order),
                fontsize=8, ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )

    # Add legend and title
    plt.title("Clusters and Dynamic Paths", fontsize=18)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.savefig(output_file, dpi=300)
    print(f"Visualization saved to {output_file}")
    plt.show()

# Load the graph and clusters
graph_path = "OptimizePath/drone_graph.json"
clusters_file = "OptimizePath/clusters.json"

with open(graph_path, "r") as f:
    graph_data = json.load(f)
with open(clusters_file, "r") as f:
    clusters = json.load(f)

G = nx.node_link_graph(graph_data)

# Sort clusters by importance and calculate tours
sorted_clusters = sort_clusters_by_importance(G, [set(cluster) for cluster in clusters])
cluster_tours = {}
for i, cluster in enumerate(sorted_clusters):
    print(f"Calculating tour for Cluster {i + 1}...")
    tour = find_tour_in_cluster_with_priority(G, cluster)
    cluster_tours[f"Cluster_{i + 1}"] = tour

# Plot clusters and their tours
plot_clusters_with_paths(G, sorted_clusters, cluster_tours)
