# ================================
# IMPORT REQUIRED MODULES
# ================================
from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsProject,
    QgsLineSymbol, QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer,
    QgsSymbol, QgsRendererCategory, QgsWkbTypes, QgsField,
    QgsCoordinateReferenceSystem, QgsRasterLayer, QgsFillSymbol
)
from qgis.PyQt.QtGui import QColor
from PyQt5.QtCore import QVariant
from qgis.core import QgsLayerTreeLayer
from shapely.geometry import Point
from pathlib import Path
import pandas as pd
import geopandas as gpd
import csv
import os
import sys

# ================================
# SETUP AND PARAMETERS
# ================================

# Maximum type value to include in the plotted segments
MAXTYPE = 5  

working_folder = Path(r'C:\temp\aziza\Direct_Indirect_Interface_V02\Direct_Indirect_Interface\Interface_Github\Output')

# Coordinate Reference System to be used (EPSG:3763 - Portuguese National Grid)
crs3763 = QgsCoordinateReferenceSystem("EPSG:3763")

# ================================
# INITIALIZE A CLEAN QGIS PROJECT
# ================================
project = QgsProject.instance()
project.setCrs(crs3763)
project.clear()  # Remove all existing layers from the project

# ================================
# LOAD THE MOST RECENT URBAN LAYER
# ================================
gpkg_files = [os.path.join(working_folder, f) for f in os.listdir(working_folder) if f.startswith("urb") and f.endswith(".gpkg")]
if gpkg_files:
    latest_gpkg = max(gpkg_files, key=os.path.getmtime)
    print("Loading urban layer:", latest_gpkg)
    urb_layer = QgsVectorLayer(latest_gpkg, os.path.basename(latest_gpkg), "ogr")
    urb_layer.setCrs(crs3763)
    if urb_layer.isValid():
        project.addMapLayer(urb_layer)
        canvas = iface.mapCanvas()
        canvas.setExtent(urb_layer.extent())  # Zoom to the layer's extent
        canvas.refresh()
        # Set fill color to semi-transparent gray
        symbol = QgsFillSymbol.createSimple({'color': 'gray', 'outline_style': 'no'})
        symbol.setColor(QColor(128, 128, 128, 128))  
        urb_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        urb_layer.triggerRepaint()
    else:
        print("Urban layer is not valid.")
else:
    print("No urban geopackage found.")

# ================================
# LOAD THE MOST RECENT FLAMMABLE LAYER
# ================================
gpkg_files = [os.path.join(working_folder, f) for f in os.listdir(working_folder) if f.startswith("flam") and f.endswith(".gpkg")]
if gpkg_files:
    latest_gpkg = max(gpkg_files, key=os.path.getmtime)
    print("Loading flammable layer:", latest_gpkg)
    flam_layer = QgsVectorLayer(latest_gpkg, os.path.basename(latest_gpkg), "ogr")
    flam_layer.setCrs(crs3763)
    if flam_layer.isValid():
        project.addMapLayer(flam_layer)
        canvas = iface.mapCanvas()
        canvas.setExtent(flam_layer.extent())  # Zoom to flammable layer
        canvas.refresh()
        # Set fill color to semi-transparent green
        symbol = QgsFillSymbol.createSimple({'color': 'green', 'outline_style': 'no'})
        symbol.setColor(QColor(128, 244, 128, 128))  
        flam_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        flam_layer.triggerRepaint()
    else:
        print("Flammable layer is not valid.")
else:
    print("No flammable geopackage found.")

# ================================
# LOAD THE MOST RECENT INTERFACE CSV
# ================================
csv_files = [os.path.join(working_folder, f) for f in os.listdir(working_folder) if f.startswith("interface") and f.endswith(".csv")]
if csv_files:
    latest_csv = max(csv_files, key=os.path.getmtime)
    print("Loading interface CSV:", latest_csv)
else:
    print("No interface CSV file found.")
    latest_csv = None

# ================================
# CREATE MEMORY POINT LAYER FROM CSV
# ================================
if latest_csv:
    df = pd.read_csv(latest_csv)

    # Extract all attribute columns except x, y (coordinates)
    fields_to_add = [col for col in df.columns if col not in ['x', 'y']]

    # Create an in-memory point layer
    point_layer = QgsVectorLayer("Point?crs=" + crs3763.authid(), "Points from CSV", "memory")
    provider = point_layer.dataProvider()

    # Add attribute fields to the layer
    provider.addAttributes([QgsField(col, QVariant.String) for col in fields_to_add])
    point_layer.updateFields()
    point_layer.startEditing()

    # Add each point from the CSV as a feature in the layer
    for _, row in df.iterrows():
        feat = QgsFeature(point_layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row['x'], row['y'])))
        for col in fields_to_add:
            feat.setAttribute(col, str(row[col]))
        provider.addFeatures([feat])

    point_layer.commitChanges()
    QgsProject.instance().addMapLayer(point_layer)

# ================================
# EXTRACT AND CONNECT SEGMENTS FROM POINTS
# ================================

# Prepare to store sequences of points forming segments
sequences = []
current_sequence = []
type_, P_, d_, x_, y_ = None, None, None, None, None
types = []

# Read through CSV again to extract point-to-point segments
with open(latest_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        x, y = float(row['x']), float(row['y'])
        P = int(row['idx_part_u'])
        type = row['vert_type']
        d = row['d']
        idx = int(row['idx_vert_u'])

        # Initialize tracking values
        if type_ is None: type_ = type
        if P_ is None: P_ = P
        if d_ is None: d_ = d
        if x_ is None: x_ = x
        if y_ is None: y_ = y

        # Same part and same type — continue sequence
        if type == type_ and P == P_:
            current_sequence.append((x, y))
            P_, d_, x_, y_ = P, d, x, y

        # Same part but type changes — close and restart sequence
        elif type != type_ and P == P_:
            mid_x, mid_y = (x + x_) * 0.5, (y + y_) * 0.5
            current_sequence.append((mid_x, mid_y))
            if len(current_sequence) >= 2 and int(type_) < MAXTYPE:
                sequences.append(current_sequence)
                types.append(str(type_))
            current_sequence = [(mid_x, mid_y), (x, y)]
            P_, d_, x_, y_, type_ = P, d, x, y, type

        # New part — close current sequence and start new
        else:
            if len(current_sequence) >= 2 and int(type_) < MAXTYPE:
                sequences.append(current_sequence)
                types.append(str(type_))
            current_sequence = [(x, y)]
            P_, d_, x_, y_, type_ = P, d, x, y, type

# Add last valid sequence
if len(current_sequence) >= 2 and int(type_) < MAXTYPE:
    sequences.append(current_sequence)
    types.append(str(type_))

# ================================
# CREATE MEMORY LINESTRING LAYER
# ================================
line_layer = QgsVectorLayer("LineString?crs=" + crs3763.authid(), "Interface", "memory")
provider = line_layer.dataProvider()
line_layer.startEditing()
provider.addAttributes([QgsField("type", QVariant.String)])
line_layer.updateFields()

# Add each sequence as a polyline feature
for i, seq in enumerate(sequences):
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in seq]))
    feat.setAttributes([types[i]])
    provider.addFeature(feat)

line_layer.commitChanges()
QgsProject.instance().addMapLayer(line_layer)

# ================================
# STYLE LINES ACCORDING TO TYPE
# ================================
categories = []
for i in range(1, MAXTYPE):
    # Define a color scheme based on type
    if i == 1:
        color = QColor(255, 0, 0)  # Red
    elif i == 3:
        color = QColor(255, 165, 0)  # Orange
    elif i == 4:
        color = QColor(255, 255, 0)  # Yellow
    else:
        r, g, b = 255, 0, 0
        if i < 3:
            g = int(165 * (i - 1) / 2)
        else:
            g = 165 + int(90 * (i - 3) / 2)
        color = QColor(r, g, b)

    # Create symbol and category
    symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
    symbol.setColor(color)
    symbol.setWidth(2)
    category = QgsRendererCategory(str(i), symbol, str(i))
    categories.append(category)

# Apply categorized renderer to the line layer
renderer = QgsCategorizedSymbolRenderer("type", categories)
line_layer.setRenderer(renderer)
line_layer.triggerRepaint()

# ================================
# ADD OSM BASEMAP (XYZ TILE LAYER)
# ================================
osm_uri = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0'
osm_layer = QgsRasterLayer(osm_uri, "OSM", "wms")
if osm_layer.isValid():
    project.addMapLayer(osm_layer, False)
    root = project.layerTreeRoot()
    root.insertChildNode(-1, QgsLayerTreeLayer(osm_layer))
else:
    print("OSM base layer failed to load!")


print("All layers loaded, styled, and added to QGIS successfully.")
