simplify = False
VisvalingamWhyatt = False
Ramer= True
################################################
#.simplify()
###############################################
if simplify : 
    import geopandas as gpd
    from shapely.geometry import Polygon
    import matplotlib.pyplot as plt

    # Helper function to simplify geometries
    def simplify_geometries(gdf, tolerance):
        gdf_simplified = gdf.copy()
        gdf_simplified["geometry"] = gdf["geometry"].apply(
            lambda geom: geom.simplify(tolerance, preserve_topology=True)
        )
        return gdf_simplified

    urban_poly = Polygon([(0, 0), (3, 1), (6, 0), (5, 4), (3, 5), (1, 4), (0, 0)])
    flamm_poly = Polygon([(4, 3), (7, 4), (9, 2), (8, 0), (6, 0), (5, 4), (4, 3)])
    urban_gdf = gpd.GeoDataFrame({'type': ['urban'], 'geometry': [urban_poly]}, crs="EPSG:3763")
    flamm_gdf = gpd.GeoDataFrame({'type': ['flammable'], 'geometry': [flamm_poly]}, crs="EPSG:3763")

    fig, ax = plt.subplots()
    urban_gdf.plot(ax=ax, color='lightblue', edgecolor='black', label="Urban (original)")
    flamm_gdf.plot(ax=ax, color='lightcoral', edgecolor='black', label="Flammable (original)")
    plt.title("Original Geometry")
    plt.legend()
    plt.show()

    SIMPLIFY_TOLERANCE = 1  # in meters or units of CRS
    urban_simplified = simplify_geometries(urban_gdf, SIMPLIFY_TOLERANCE)
    flamm_simplified = simplify_geometries(flamm_gdf, SIMPLIFY_TOLERANCE)

    fig, ax = plt.subplots()
    urban_simplified.plot(ax=ax, color='blue', alpha=0.5, edgecolor='black', label="Urban (simplified)")
    flamm_simplified.plot(ax=ax, color='red', alpha=0.5, edgecolor='black', label="Flammable (simplified)")
    plt.title(f"Simplified Geometry (tolerance={SIMPLIFY_TOLERANCE})")
    plt.legend()
    plt.show()

    print("Original Urban Vertices:", len(urban_poly.exterior.coords))
    print("Simplified Urban Vertices:", len(urban_simplified.geometry.iloc[0].exterior.coords))
    print("Original Flammable Vertices:", len(flamm_poly.exterior.coords))
    print("Simplified Flammable Vertices:", len(flamm_simplified.geometry.iloc[0].exterior.coords))

################################################
# Ramer-Douglas-Peucker (RDP)
################################################
if Ramer: 
    import geopandas as gpd
    from shapely.geometry import Polygon
    from rdp import rdp
    import numpy as np
    import matplotlib.pyplot as plt
    urban_coords = [(0, 0), (3, 1), (6, 0), (5, 4), (3, 5), (1, 4), (0, 0)]
    flamm_coords = [(4, 3), (7, 4), (9, 2), (8, 0), (6, 0), (5, 4), (4, 3)]
    urban_poly = Polygon(urban_coords)
    flamm_poly = Polygon(flamm_coords)
    # Apply RDP simplification
    def simplify_rdp(polygon, epsilon=1.0):
        coords = np.array(polygon.exterior.coords)
        simplified_coords = rdp(coords, epsilon=epsilon)
        return Polygon(simplified_coords)

    # Simplify with RDP
    epsilon = 1.0  # tolerance in coordinate units (e.g., meters)
    urban_simple = simplify_rdp(urban_poly, epsilon)
    flamm_simple = simplify_rdp(flamm_poly, epsilon)
    gdf_urban = gpd.GeoDataFrame(geometry=[urban_poly], crs="EPSG:3763")
    gdf_urban_s = gpd.GeoDataFrame(geometry=[urban_simple], crs="EPSG:3763")
    gdf_flamm = gpd.GeoDataFrame(geometry=[flamm_poly], crs="EPSG:3763")
    gdf_flamm_s = gpd.GeoDataFrame(geometry=[flamm_simple], crs="EPSG:3763")
    fig, ax = plt.subplots()
    gdf_urban.plot(ax=ax, facecolor='lightblue', edgecolor='black', label="Urban (original)")
    gdf_urban_s.plot(ax=ax, facecolor='none', edgecolor='blue', linestyle='--', label="Urban (RDP simplified)")
    plt.title("Urban Polygon: RDP Simplification")
    plt.legend()
    plt.show()
    fig, ax = plt.subplots()
    gdf_flamm.plot(ax=ax, facecolor='lightcoral', edgecolor='black', label="Flammable (original)")
    gdf_flamm_s.plot(ax=ax, facecolor='none', edgecolor='red', linestyle='--', label="Flammable (RDP simplified)")
    plt.title("Flammable Polygon: RDP Simplification")
    plt.legend()
    plt.show()
    print("Original Urban Vertices:", len(urban_coords))
    print("Simplified Urban Vertices:", len(urban_simple.exterior.coords))
    print("Original Flammable Vertices:", len(flamm_coords))
    print("Simplified Flammable Vertices:", len(flamm_simple.exterior.coords))

################################################
# simplification package (Visvalingam-Whyatt)
################################################
if VisvalingamWhyatt: 
    import numpy as np
    from shapely.geometry import Polygon
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from simplification.cutil import simplify_coords_vw

    # polygon
    coords = [(0, 0), (2, 0.1), (3, 0.3), (4, 0.1), (6, 0), (5, 4), (3, 5), (1, 4), (0, 0)]
    polygon = Polygon(coords)
    path = np.array(coords)
    # Apply Visvalingam-Whyatt simplification (area threshold)
    simplified_path = simplify_coords_vw(path, epsilon=0.3)  # try 0.1 to 1.0 for tuning
    # Rebuild simplified polygon
    simplified_polygon = Polygon(simplified_path)
    gdf_original = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:3763")
    gdf_simplified = gpd.GeoDataFrame(geometry=[simplified_polygon], crs="EPSG:3763")
    fig, ax = plt.subplots()
    gdf_original.plot(ax=ax, edgecolor='black', facecolor='lightgray', label="Original")
    gdf_simplified.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=2, label="Simplified")
    plt.title("Visvalingam–Whyatt Simplification")
    plt.legend()
    plt.show()
    print("Original vertex count:", len(polygon.exterior.coords))
    print("Simplified vertex count:", len(simplified_polygon.exterior.coords))
