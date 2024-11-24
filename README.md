Y-AQUILA Algorithm

This document presents a streamlined process for optimizing drone operations in disaster-affected areas using geospatial data and advanced algorithms. By extracting and analyzing Copernicus data, the system creates prioritized grid zones and generates an optimal path for drones, focusing on high-impact areas while considering operational constraints like battery life and range.
Key steps include data processing, grid creation, priority scoring, clustering, and path optimization, all automated through custom scripts. This approach ensures efficient coverage of critical zones, minimizing travel distances and maximizing impact, offering a practical solution for emergency response teams.


Data Analysis and Download

Each disaster is associated with an activation ID consisting of a few digits (for example, for the Valencia floods, the ID is 773).
The first step is to download the Copernicus data associated with an activation ID. This is done through the Copernicus API (OpenAPI) using the URL: https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations/ and the code: EMSR followed by the ID (e.g., EMSR773 for Valencia).
We download this data using our download_data.py script into a local folder: copernicus_data.
Since the data is stored in ZIP format, we need to extract it into a new folder: copernicus_extracted.
 Additionally, due to the large volume of data, we optimize our usage by focusing only on these five pieces of information:
geometry: Geographical shapes (areas to grid).
event_type: Type of event (flood, fire, etc.).
area: Surface area of the impacted region.
obj_type: Type of infrastructure affected (if available).
damage_pref: Level of damage (to prioritize critical areas).
These data points already provide a clear overview of the situation and are sufficient for our needs.
 We then filter the documents, extracting these five key pieces of information into .geojson files, all stored in the folder filtered_data.
All these operations are carried out using our data_filter.py script.
Next, we use the data_filter2.py script to retain only the documents from filtered_data that have boundaries. These files are then stored in the filtered_data2 folder.
Finally, using the scripts data_filter3.py, filtrage_aoi.py, filtrage_del.py, filtrage_obj_type.py, and filtre_event_type.py, we create the following folders:
filtered_data_3, which filters files from data_filter2.py that include event types or residential areas (11 - Residential Buildings).
filtered_data_aoi_only: Focuses solely on the Areas of Interest (AOIs) identified during the filtering process.
merged_event_data.geojson: Combines flood-related data into a single file representing affected flood areas.
merged_obj_data.geojson: Merges data related to residential and other relevant infrastructure into one file.

Thanks to this process, we obtain the three most important datasets:
AOIs in the filtered_data_aoi_only folder.
Flood areas in the merged_event_data.geojson file.
Residential areas in the merged_obj_data.geojson file.
Zone Gridding Section

The goal is now to grid the area of interest by creating a mesh where each cell has a priority score, which will be useful for generating an optimal path later.
The make_grille.py script generates a global_filtered_grid.geojson file that represents all the cells containing flood areas.
Each cell has a side length of 500 meters. This length was specifically chosen to ensure that a cell represents an area where the drone can locate everyone. Below are the detailed calculations justifying this choice:

Step 1: Determining the Diameter of the Coverage Zone
The Directional Finder + IMSI-Catcher system has a field of view angle of 100 degrees. The drone's altitude is approximately 300 meters.
The coverage zone of the sensor forms a cone, and the base of this cone is a circle. The diameter D of the cone's base is calculated as:




Step 2: Converting the Circle into a Square
The circle with a diameter of 715 meters can be used to create a square that fits inside this circle. The diagonal of the square corresponds to the circle's diameter, i.e., D=715 m. The side length L of a square with a known diagonal can be calculated using the Pythagorean theorem:



Thus, each cell has a side length of 500 meters, ensuring that the entire area covered by a cell is fully within the sensor's field of view.
With this, we have a grid for the area to be processed.


Assigning Importance Scores to Each Cell
The next step involves assigning an importance score to each grid cell to determine the priority for drone coverage. This score helps identify which areas require the drone's attention first.

We use the make_cell_score.py script to calculate an importance score for each cell. The score is based on the ratio of residential areas affected by flooding within the boundaries of each cell. The higher this ratio, the higher the priority score assigned to the cell. The scoring follows a linear relationship, ensuring simplicity and clarity in the prioritization process.
The script takes two key data inputs:
The gridded cells from global_filtered_grid.geojson.
Layers containing information about flooded areas and residential zones from merged_event_data.geojson and merged_obj_data.geojson.
For each cell, it checks the intersection of its geometry with the flood zones and residential areas. This is done using spatial analysis functions, such as geometric intersection and area calculation.
The resulting cell_scores.geojson file is a comprehensive representation of the gridded area, where each cell is annotated with its priority score. This file is crucial for subsequent steps, such as optimizing the drone’s flight path to efficiently cover the most critical areas.



Optimizing Drone Path in the Area
The goal is now to determine the optimal path for a drone to follow, prioritizing cells with high scores. This involves transforming the data, building a graph structure, and assigning weights to prioritize critical areas.
To streamline calculations, the cell_scores.geojson file is converted into cell_scores_centroid.geojson. In this step:
The center (centroid) of each cell is extracted.
These centroids are saved as individual points, reducing the complexity of working with polygons.
Using the make_graph.py script, a graph is created where each centroid becomes a node in the graph and the distance between centroids is used to define edges between nodes. 
Only centroids within 3000 meters of each other are connected by edges. This threshold ensures the graph remains lightweight and computationally manageable while maintaining relevant connections. The weight of each node is the priority score of the previous cell. 
This transformation ensures that subsequent calculations and graph construction are faster and more efficient.

The next step is to select the optimal traversal path through the graph. This path must account for both the distances between nodes and their importance. 
Since the drone has limited battery life, it cannot cover excessively large distances solely based on priority scores. 
In practice, we observe that several distant areas have high-priority cells, making it essential to divide the area into clusters.




Using the create_cluster.py script, we define zones of interest based on two parameters: a score threshold and a maximum distance. Nodes with a priority score exceeding the threshold are designated as the starting points of clusters. 
The script then expands each cluster by including nearby nodes within the specified maximum distance. If two clusters overlap, they merge to form a single, larger cluster. This process ensures that clusters represent both critical areas (defined by high scores) and practical boundaries (based on the drone’s range).
For this implementation, we used a score threshold of 0.2 and a maximum distance of 3000 meters. These values were chosen to align with the drone's autonomy and speed, ensuring efficient and realistic operation. However, they can be adjusted based on specific drone capabilities or mission requirements.
The resulting clusters, stored in clusters.json, provide a clear and manageable framework for planning efficient drone paths within operational limits.

Finally, the path.py script generates the optimal path for the drone to follow.
The process begins by ranking the clusters based on their priority, calculated as the sum of the priority scores of all the cells within each cluster. This ensures that the most critical clusters, with the highest cumulative importance, are addressed first during drone operations.

Within each cluster, since the distances between nodes are feasible for the drone, the path is determined by the importance scores of the nodes. The drone follows the nodes in descending order of priority, ensuring that the most significant areas within each cluster are covered first.




The main.py script automates the entire process, from data preparation to generating the optimal drone path. It integrates all the steps, including data filtering, grid creation, clustering, and path optimization, into a single streamlined workflow.
The Show folder contains the functions used to visualize the results, allowing for the display of maps and graphs generated throughout the process, providing clear insights into the processed data and the drone's planned operations.











