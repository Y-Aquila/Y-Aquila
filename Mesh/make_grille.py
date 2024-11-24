import os
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import math


AOI_DIR = "DATA/filtered_data_aoi_only"  
EVENT_DIR = "DATA/filtered_event_data"  
OUTPUT_GRID_FILE = "global_filtered_grid.geojson" 
CELL_SIZE_METERS = 500  

def meters_to_degrees(cell_size_meters, latitude):

    # Latitude conversion
    cell_size_lat = cell_size_meters / 111_000  # 1° de latitude = 111 km

    # Longitude conversion
    cell_size_lon = cell_size_meters / (111_320 * math.cos(math.radians(latitude)))

    return cell_size_lat, cell_size_lon

def get_reference_latitude(aoi_dir):

    latitudes = []

    for file_name in os.listdir(aoi_dir):
        file_path = os.path.join(aoi_dir, file_name)
        if file_path.endswith(".geojson"):
            gdf = gpd.read_file(file_path)
            if not gdf.empty and "geometry" in gdf.columns:
                latitudes.extend([geom.centroid.y for geom in gdf.geometry if geom is not None])

    if latitudes:
        return sum(latitudes) / len(latitudes)  # Latitude mean
    else:
        raise ValueError("Impossible to calcul a reference latitude because of AOIs.")

def create_union_of_aois(aoi_dir):

    all_aois = []

    for file_name in os.listdir(aoi_dir):
        file_path = os.path.join(aoi_dir, file_name)
        if file_path.endswith(".geojson"):
            gdf = gpd.read_file(file_path)
            if not gdf.empty and "geometry" in gdf.columns:
                all_aois.append(gdf.unary_union)

    if all_aois:
        return gpd.GeoSeries(all_aois).unary_union  # AOIs global union
    else:
        raise ValueError("No valid AOIs.")

def create_grid_from_union(union_polygon, cell_size_lat, cell_size_lon):

    bounds = union_polygon.bounds  # xmin, ymin, xmax, ymax
    x_min, y_min, x_max, y_max = bounds
    x_coords = np.arange(x_min, x_max, cell_size_lon)
    y_coords = np.arange(y_min, y_max, cell_size_lat)

    cells = []
    for x in x_coords:
        for y in y_coords:
            cell = Polygon([
                (x, y),
                (x + cell_size_lon, y),
                (x + cell_size_lon, y + cell_size_lat),
                (x, y + cell_size_lat),
                (x, y)
            ])
            if cell.intersects(union_polygon):  
                cells.append(cell)

    grid_gdf = gpd.GeoDataFrame(geometry=cells, crs="EPSG:4326")
    return grid_gdf

def filter_grid_with_events(grid_gdf, event_dir):

    all_events = []

    for file_name in os.listdir(event_dir):
        file_path = os.path.join(event_dir, file_name)
        if file_path.endswith(".geojson"):
            gdf = gpd.read_file(file_path)
            if not gdf.empty and "geometry" in gdf.columns:
                all_events.append(gdf.unary_union)

    if all_events:
        events_union = gpd.GeoSeries(all_events).unary_union  
        filtered_cells = grid_gdf[grid_gdf.intersects(events_union)]  
        return filtered_cells
    else:
        print("Aucune zone d'inondation trouvée pour filtrer la grille.")
        return grid_gdf 

# Main steps
try:
    print("Reference altitude calcul...")
    LATITUDE_REFERENCE = get_reference_latitude(AOI_DIR)
    print(f"Reference Latitude : {LATITUDE_REFERENCE}")

    print("Size of cell conversion in degrees...")
    cell_size_lat, cell_size_lon = meters_to_degrees(CELL_SIZE_METERS, LATITUDE_REFERENCE)

    print("AOIs union creation...")
    union_aoi = create_union_of_aois(AOI_DIR)

    print("Global grid creation...")
    global_grid = create_grid_from_union(union_aoi, cell_size_lat, cell_size_lon)

    print("Filtering the grid with event areas...")
    filtered_grid = filter_grid_with_events(global_grid, EVENT_DIR)

    filtered_grid.to_file(OUTPUT_GRID_FILE, driver="GeoJSON")

except Exception as e:
    print(f"Error : {e}")
