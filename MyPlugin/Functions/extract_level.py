##############################################
    #    Main Library       #  
##############################################
import pandas as pd

##############################################
    #    Main Function       #  
##############################################
def extract_vertices(geodf):
    """
    Extract levels and coordinates from a GeoDataFrame.
    
    MULTIPOLYGON:
    L1 identifies main rings or holes ==> outer polygon or hole
    L2 specifies the ring ID within a particular polygon of the multipolygon ==> part
    L3 distinguishes between different multipolygons ==> feature
    
    The output is a pandas dataFrame
    """
    data = []
    for feature_index, geom in enumerate(geodf.geometry, start=1):  # Iterate over each geometry in the GeoDataFrame
        if geom is None:
            continue
        if geom.geom_type == 'MultiPolygon':  # Iterate over each Polygon in a MultiPolygon
            for part_index, poly in enumerate(geom.geoms, start=1):
                # Extract the exterior ring 
                exterior_coords = poly.exterior.coords
                for ring_index, (x, y) in enumerate(exterior_coords, start=1):
                    data.append([x, y, 1, part_index, feature_index])
                # Iterate over interior rings (holes)
                for interior_index, interior in enumerate(poly.interiors, start=1):
                    interior_coords = interior.coords
                    for ring_index, (x, y) in enumerate(interior_coords, start=1):
                        data.append([x, y, interior_index+1, part_index, feature_index])
        elif geom.geom_type == 'Polygon': 
            # Extract exterior ring of a single Polygon
            exterior_coords = geom.exterior.coords
            for ring_index, (x, y) in enumerate(exterior_coords, start=1):
                data.append([x, y, 1, 1, feature_index])
            # Extract interior rings (holes)
            for interior_index, interior in enumerate(geom.interiors, start=1):
                interior_coords = interior.coords
                for ring_index, (x, y) in enumerate(interior_coords, start=1):
                    data.append([x, y, interior_index+1, 1, feature_index])
        else:
            print(f"Unsupported geometry type: {geom.geom_type}")
    
    df = pd.DataFrame(data, columns=['x', 'y', 'L1', 'L2', 'L3'])
    return df

