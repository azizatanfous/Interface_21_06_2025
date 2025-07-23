##############################################
    #    Libraries       #  
##############################################
from shapely.ops import nearest_points
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
##############################################
    #    Main Function       #  
##############################################
def convert_xy(X, Y, urban_path):
    # Load the urban geometries
    urb = gpd.read_file(urban_path)

    # Create a Point object from input coordinates
    target_point = Point(X, Y)

    # Create a GeoSeries of polygon boundaries
    boundaries = urb.geometry.boundary

    # Compute distances to the target point
    distances = boundaries.distance(target_point)

    # Get the geometry with the minimum distance
    min_idx = distances.idxmin()

    # Compute the nearest point on the boundary
    nearest_pt = nearest_points(boundaries[min_idx], target_point)[0]

    # Return as a DataFrame
    return pd.DataFrame([{'X': nearest_pt.x, 'Y': nearest_pt.y}])