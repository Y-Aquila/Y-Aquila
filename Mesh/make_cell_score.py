import geopandas as gpd

GRID_FILE = "global_filtered_grid.geojson"  
INTERSECTION_FILE = "event_obj_intersection.geojson"  
OUTPUT_SCORES_FILE = "cell_scores.geojson" 

def calculate_building_flood_scores_with_union(grid_file, intersection_file, output_file):

    grid_gdf = gpd.read_file(grid_file).to_crs("EPSG:32633")
    building_flood_intersection = gpd.read_file(intersection_file).to_crs(grid_gdf.crs)

    global_union = building_flood_intersection.unary_union

    grid_gdf["cell_area"] = grid_gdf.geometry.area

    grid_gdf["building_event_area"] = 0.0


    for idx, cell in grid_gdf.iterrows():

        intersection = cell.geometry.intersection(global_union)

        if not intersection.is_empty:

            total_area = intersection.area
            print(f"Cell {idx} : Total intersection area = {total_area}")
            grid_gdf.loc[idx, "building_event_area"] = total_area
        else:
            print(f"Cell {idx} : 0 intersection.")

    print("Final score calcul")
    grid_gdf["score"] = grid_gdf["building_event_area"] / grid_gdf["cell_area"]

    grid_gdf = grid_gdf.to_crs("EPSG:4326")

    # Save in a GeoJSON folder
    grid_gdf.to_file(output_file, driver="GeoJSON")

# Exécution de la fonction
calculate_building_flood_scores_with_union(GRID_FILE, INTERSECTION_FILE, OUTPUT_SCORES_FILE)
