import pandas as pd

def extract_urb_vertices_and_buffered(geodf,col,value):
    """
    Extract levels and coordinates from a GeoDataFrame.
    
    The output is a pandas dataFrame, with an extra column 'buffered'.
    """
    data = []
    for feature_index, (geom, layer) in enumerate(zip(geodf.geometry, geodf[col]), start=1):
        if geom is None:
            continue
        if geom.geom_type == 'MultiPolygon':
            for part_index, poly in enumerate(geom.geoms, start=1):
                # Extract the exterior ring 
                exterior_coords = poly.exterior.coords
                for ring_index, (x, y) in enumerate(exterior_coords, start=1):
                    data.append([x, y, 1, part_index, feature_index, 1 if layer == value else 0])
                # Iterate over interior rings (holes)
                for interior_index, interior in enumerate(poly.interiors, start=1):
                    interior_coords = interior.coords
                    for ring_index, (x, y) in enumerate(interior_coords, start=1):
                        data.append([x, y, interior_index+1, part_index, feature_index, 1 if layer == value else 0])
        elif geom.geom_type == 'Polygon': 
            # Extract exterior ring of a single Polygon
            exterior_coords = geom.exterior.coords
            for ring_index, (x, y) in enumerate(exterior_coords, start=1):
                data.append([x, y, 1, 1, feature_index, 1 if layer == value else 0])
            # Extract interior rings (holes)
            for interior_index, interior in enumerate(geom.interiors, start=1):
                interior_coords = interior.coords
                for ring_index, (x, y) in enumerate(interior_coords, start=1):
                    data.append([x, y, interior_index+1, 1, feature_index, 1 if layer == value else 0])
        else:
            print(f"Unsupported geometry type: {geom.geom_type}")
    
    df = pd.DataFrame(data, columns=['x', 'y', 'L1', 'L2', 'L3', 'buffered'])
    return df