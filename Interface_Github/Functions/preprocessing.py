##############################################
    #    Libraries       #  
##############################################
from shapely.geometry import MultiPolygon,box
import numpy as np


##############################################
    #    Preprocessing Functions     #  
##############################################

# Converts all single Polygon geometries in a GeoDataFrame to MultiPolygon
def promote_to_multipolygon(gdf):
    """
    Input:
    gdf (GeoDataFrame): A GeoPandas GeoDataFrame containing geometries.

    Output:
    GeoDataFrame: The modified GeoDataFrame where all single Polygons are converted to MultiPolygons.
    """
    if gdf.geom_type.str.contains("Polygon").any():
        gdf["geometry"] = gdf["geometry"].apply(lambda geom: MultiPolygon([geom]) if geom.geom_type == "Polygon" else geom)
    return gdf

def process_flammables(flam, BOX):
    """
    Input:
    flam (GeoDataFrame): The input GeoDataFrame containing geometries.
    BOX (dict): The bounding box for selection.

    Output:
    GeoDataFrame: The processed GeoDataFrame with only Polygons (or optionally MultiPolygons) that intersect the bounding box.
    """
    # Create the bounding box polygon
    bounding_polygon = box(BOX["xmin"], BOX["ymin"], BOX["xmax"], BOX["ymax"])
    # Explode all MultiPolygons into individual Polygons (preserves topology)
    exploded = flam.explode(index_parts=False)#[1]
    # Select only the Polygons that intersect the bounding box
    intersects = exploded.intersects(bounding_polygon)
    result = exploded[intersects].copy()
    # If you want to group back into MultiPolygons (optional, may not be needed)
    # result["idx_group"] = result.index.get_level_values(0)  # Use the original index for grouping
    # result = result.dissolve(by="idx_group", as_index=False)
    # Note: Dissolve may not preserve all attributes, so only use if necessary
    return result

# Removes duplicate
def clean_and_reindex(df, part_col, vert_col):
    """
    Input:
    df (pd.DataFrame): DataFrame containing spatial data.
    part_col (str):  (e.g., 'idx_part_flam' or 'idx_part_urb').
    vert_col (str):  (e.g., 'idx_vert_flam' or 'idx_vert_urb').

    Output:
    pd.DataFrame: Processed DataFrame with duplicates removed and the vertex column reindexed.
    """
    dups = df.duplicated() 
    step = np.append(np.diff(df[part_col].values) != 0, False)  
    df = df.loc[~(dups & ~step)].copy()  

    df.loc[:, vert_col] = np.arange(1, len(df) + 1)  

    return df  

def insert_zero_at_the_beginning_of_1D_array(arr):
    return np.insert(arr, 0, 0)
    
def insert_bigN_at_the_beginning_of_1D_array(arr):
    return np.insert(arr, 0, 10**6)