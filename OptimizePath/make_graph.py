import geopandas as gpd
import networkx as nx
from geopy.distance import geodesic
from tqdm import tqdm
import json

# Charger le GeoJSON des points
input_path = "OptimizePath/cell_scores_centroid.geojson"
gdf = gpd.read_file(input_path)

print("Création Graphe...")
# Créer un graphe
G = nx.Graph()

print("Ajout des noeuds...")
# Ajouter les nœuds au graphe avec leurs scores comme attribut
for index, row in gdf.iterrows():
    node_id = index  # Utiliser l'index comme identifiant unique
    position = (row.geometry.y, row.geometry.x)  # Latitude et longitude
    score = row['score']  # Remplace 'score' par le nom de l'attribut dans ton fichier
    G.add_node(node_id, position=position, score=score)

print("Ajout des arêtes (voisins à moins de 3000m)...")
# Ajouter des arêtes uniquement pour les voisins situés à moins de 3000m
nodes = list(G.nodes(data=True))
for i in tqdm(range(len(nodes))):
    for j in range(i + 1, len(nodes)):
        node1 = nodes[i]
        node2 = nodes[j]
        pos1 = node1[1]['position']
        pos2 = node2[1]['position']
        distance = geodesic(pos1, pos2).meters  # Calculer la distance en mètres

        # Ajouter une arête uniquement si la distance est <= 3000m
        if distance <= 3000:
            G.add_edge(node1[0], node2[0], weight=distance)

print("Graphe créé avec succès !")
print(f"Nombre de nœuds : {G.number_of_nodes()}, Nombre d'arêtes : {G.number_of_edges()}")

print("Enregistrement du graphe en JSON...")
# Convertir le graphe en dictionnaire
graph_data = nx.node_link_data(G)

# Enregistrer le graphe en JSON
output_path = "OptimizePath/drone_graph.json"
with open(output_path, "w") as f:
    json.dump(graph_data, f, indent=4)

print(f"Graphe enregistré avec succès dans {output_path} !")
