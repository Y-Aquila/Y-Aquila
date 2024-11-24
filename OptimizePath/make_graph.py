import geopandas as gpd
import networkx as nx
from geopy.distance import geodesic
from tqdm import tqdm
import json

# Load the GeoJSON file with points
input_path = "OptimizePath/cell_scores_centroid.geojson"
gdf = gpd.read_file(input_path)

print("Creating graph...")
# Create a graph
G = nx.Graph()

print("Adding nodes...")
# Add nodes to the graph with their scores as attributes
for index, row in gdf.iterrows():
    node_id = index  # Use the index as a unique identifier
    position = (row.geometry.y, row.geometry.x)  # Latitude and longitude
    score = row['score']  # Replace 'score' with the attribute name in your file
    G.add_node(node_id, position=position, score=score)

print("Adding edges (neighbors within 3000m)...")
# Add edges only for neighbors within 3000m
nodes = list(G.nodes(data=True))
for i in tqdm(range(len(nodes))):
    for j in range(i + 1, len(nodes)):
        node1 = nodes[i]
        node2 = nodes[j]
        pos1 = node1[1]['position']
        pos2 = node2[1]['position']
        distance = geodesic(pos1, pos2).meters  # Calculate the distance in meters

        # Add an edge only if the distance is <= 3000m
        if distance <= 3000:
            G.add_edge(node1[0], node2[0], weight=distance)

print("Graph successfully created!")
print(f"Number of nodes: {G.number_of_nodes()}, Number of edges: {G.number_of_edges()}")

print("Saving graph to JSON...")
# Convert the graph to a dictionary
graph_data = nx.node_link_data(G)

# Save the graph to JSON
output_path = "OptimizePath/drone_graph.json"
with open(output_path, "w") as f:
    json.dump(graph_data, f, indent=4)

print(f"Graph successfully saved to {output_path}!")
