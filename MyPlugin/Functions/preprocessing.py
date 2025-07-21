##############################################
    #    Libraries       #  
##############################################
from shapely.geometry import MultiPolygon,box
import geopandas as gpd
import pandas as pd
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


# Processes the  GeoDataFrame 
def process_flammables(flam, BOX):
    """
    Input:
    flam (GeoDataFrame): The input GeoDataFrame containing  geometries.
    bounding_box (dic): The bounding box for cropping.

    Output:
    GeoDataFrame: The processed GeoDataFrame with MultiPolygon geometries.
    """
    
    bounding_polygon = box(BOX["xmin"], BOX["ymin"], BOX["xmax"], BOX["ymax"])
    flam = flam.clip(bounding_polygon)  # Crop the GeoDataFrame 

    auxflam = flam[flam.geom_type == "MultiPolygon"]  # Select MultiPolygons 
    polyflam = auxflam.explode(index_parts=False)  # Convert MultiPolygons to individual Polygons

    geomcolname = flam.geometry.name  
    newgeomcolname = polyflam.geometry.name  

    if newgeomcolname != geomcolname:
        polyflam = polyflam.rename_geometry(geomcolname) 

    flam = pd.concat([flam[flam.geom_type == "Polygon"], polyflam], ignore_index=True)  # Merge Polygons with exploded ones
    flam["geometry"] = flam["geometry"].apply(lambda geom: MultiPolygon([geom]) if geom.geom_type == "Polygon" else geom)  # Convert Polygons to MultiPolygons

    return flam  

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

