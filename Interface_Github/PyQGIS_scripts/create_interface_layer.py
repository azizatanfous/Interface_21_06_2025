from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsProject
from qgis.core import QgsLineSymbol, QgsSingleSymbolRenderer
from qgis.core import QgsCategorizedSymbolRenderer, QgsSymbol, QgsRendererCategory, QgsWkbTypes
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsVectorLayer, QgsFeature, QgsPointXY, QgsGeometry, QgsField, QgsProject, QgsCoordinateReferenceSystem
from PyQt5.QtCore import QVariant
from qgis.core import QgsRasterLayer, QgsProject
from shapely.geometry import Point
from pathlib import Path
import pandas as pd
import geopandas as gpd
import csv
import sys
import os


MAXTYPE=5 # automatize (all segments withtype higher or equal than this won't be plotted)
working_folder = Path(r'C:\temp\aziza\Direct_Indirect_Interface_V02\Direct_Indirect_Interface\Interface_Github\Output')  # <-- Update this path
#working_folder = Path(r'C:\Users\mlc\OneDrive\Documents\temp\interface_smos\interface_python\Interface_Github\Output')  # <-- Update this path# <-- Update this path
#filename='interface_K5_KF5_limiar105_maxtheta60_QT10_test-AR2019.csv'
#csv_path= working_folder/filename

# 1. Clear all layers from the project
crs3763 = QgsCoordinateReferenceSystem("EPSG:3763")
project = QgsProject.instance()
project.setCrs(crs3763)
project.clear()  # Clears the project, including all layers[1][3][7]

# CRS for layers
project = QgsProject.instance()
project.setCrs(crs3763)


########################################################################
# urb & flam
# 2. Find the most recent geopackage starting with "urb"
file_pattern = "urb*.gpkg"
gpkg_files = [os.path.join(working_folder, f) for f in os.listdir(working_folder) if f.startswith("urb") and f.endswith(".gpkg")]

if not gpkg_files:
    print("No geopackage files found starting with 'urb'")
else:
    # Get the most recent file by modification time
    latest_gpkg = max(gpkg_files, key=lambda x: os.path.getmtime(x))
    print("Loading:", latest_gpkg)

# 3. Load the geopackage
layer = QgsVectorLayer(latest_gpkg, os.path.basename(latest_gpkg), "ogr")
layer.setCrs(crs3763)
if not layer.isValid():
    print("Failed to load layer:", latest_gpkg)
else:
    project.addMapLayer(layer)
    # 4. Zoom to the layer extent
    canvas = iface.mapCanvas()
    canvas.setExtent(layer.extent())
    canvas.refresh()
    # 5. Set polygon fill color to green for all features
    symbol = QgsFillSymbol.createSimple({'color': 'gray', 'outline_style': 'no'}) # gray with 50% transp ( higher alpha = more opaque)
    symbol.setColor(QColor(128, 128, 128, 128)) ## gray 50% opaque
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()

########################################################################
# flam
# find the most recent geopackage starting with "flam"
file_pattern = "urb*.gpkg"
gpkg_files = [os.path.join(working_folder, f) for f in os.listdir(working_folder) if f.startswith("flam") and f.endswith(".gpkg")]

if not gpkg_files:
    print("No geopackage files found starting with 'urb'")
else:
    # Get the most recent file by modification time
    latest_gpkg = max(gpkg_files, key=lambda x: os.path.getmtime(x))
    print("Loading:", latest_gpkg)

# 3. Load the geopackage
layer = QgsVectorLayer(latest_gpkg, os.path.basename(latest_gpkg), "ogr")
layer.setCrs(crs3763)
if not layer.isValid():
    print("Failed to load layer:", latest_gpkg)
else:
    project.addMapLayer(layer)
    # 4. Zoom to the layer extent
    canvas = iface.mapCanvas()
    canvas.setExtent(layer.extent())
    canvas.refresh()
    # 5. Set polygon fill color to green for all features
    symbol = QgsFillSymbol.createSimple({'color': 'green', 'outline_style': 'no'}) # light green 60% opaque
    symbol.setColor(QColor(128, 244, 128, 128)) ## light green 50% opaque
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


##############################################################
# interface
# read csv
file_pattern = "interface*.csv"
csv_files = [os.path.join(working_folder, f) for f in os.listdir(working_folder) if f.startswith("interface") and f.endswith(".csv")]

if not csv_files:
    print("No csv files found starting with 'interface'")
else:
    # Get the most recent file by modification time
    latest_csv = max(csv_files, key=lambda x: os.path.getmtime(x))
    print("Loading:", latest_csv)
    
print(latest_csv)

## create point layer from csv file 
import pandas as pd


# Read CSV (adjust path as needed)
df = pd.read_csv(latest_csv)

# Remove 'x' and 'y' from fields if present
fields_to_add = [col for col in df.columns if col not in ['x', 'y']]

# Create memory layer
layer = QgsVectorLayer("Point?crs="+ crs3763.authid(), "Memory Layer", "memory")
layer.setCrs(crs3763)
provider = layer.dataProvider()

# Add fields
for col in fields_to_add:
    # Guess the field type (for simplicity, all are set to String in this example)
    provider.addAttributes([QgsField(col, QVariant.String)])
layer.updateFields()

# Add features
layer.startEditing()
for _, row in df.iterrows():
    feat = QgsFeature(layer.fields())
    # Set geometry
    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row['x'], row['y'])))
    # Set attributes
    for col in fields_to_add:
        feat.setAttribute(col, str(row[col]))
    provider.addFeatures([feat])
layer.commitChanges()


###################################################################  compute segments
sequences = []
current_sequence = []
# moving current values
type_ = None
P_=None # part
d_=None
x_=None
y_=None
types=[]
with open(latest_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        x = float(row['x'])
        y = float(row['y'])
        P = int(row['idx_part_u'])
        type = row['vert_type']
        d = row['d']
        idx=row['idx_vert_u']
        if int(idx)==257 or int(idx)==258:
            print('---------------------------------')
            print(x,y,P,type,d,idx)
        # If current_type is None, start a new sequence with this type
        if type_ is None: type_ = type
        if P_ is None: P_ = P
        if d_ is None: d_ = d
        if x_ is None: x_ = x
        if y_ is None: y_ = y
        # If the current row matches the current sequence type and both links are 1
        if type == type_ and P==P_:
            current_sequence.append((x, y))  
            P_,d_,x_,y_=P,d,x,y
        elif (type != type_) and P==P_:
            # creates new vertex, closes segment, starts new one
            _x=(x+x_)*0.5
            _y=(y+y_)*0.5
            if int(idx)==257 or int(idx)==258:
                print('-------+-------------+-------+-----')
                print(x_,y_,x,y,_x,_y,type)
            current_sequence.append((_x,_y))
            if len(current_sequence) >= 2 and int(type_)<MAXTYPE:
                sequences.append(current_sequence)
                types.append(str(type_))
            # start a new sequence
            current_sequence=[(_x,_y)]
            current_sequence.append((x,y))
            P_,d_,x_,y_,type_=P,d,x,y,type
        else: # same as P!=P_
            # If the sequence is broken, add it if it has at least 2 points
            if len(current_sequence) >= 2 and int(type_)<MAXTYPE:
                sequences.append(current_sequence)
                types.append(str(type_)) # type for the sequence
            # start a new sequence
            current_sequence = [(x,y)]
            P_,d_,x_,y_,type_=P,d,x,y,type
            
# Add the last sequence if it's valid
if len(current_sequence) >= 2 and int(type_)<MAXTYPE:
    sequences.append(current_sequence)
    types.append(str(type_))

# 
xyd = QgsVectorLayer("LineString?crs="+ crs3763.authid(), "linestrings", "memory")
xyd.setCrs(crs3763)
provider = xyd.dataProvider()

# Add the "length" field to the layer
xyd.startEditing()
provider.addAttributes([
    #QgsField("length", QVariant.Int),
    QgsField("type", QVariant.String)
    ])  # Use QVariant.Double if lengths are not integers
xyd.updateFields()

#Add features with their corresponding lengths
for i, seq in enumerate(sequences):
    feat = QgsFeature()
    points = [QgsPointXY(x, y) for x, y in seq]
    geom = QgsGeometry.fromPolylineXY(points)
    feat.setGeometry(geom)
    feat.setAttributes([types[i]])  # Set the "type" attribute
    provider.addFeature(feat)

xyd.commitChanges()  # Save changes

QgsProject.instance().addMapLayer(xyd)

categories = []
for i in range(1, MAXTYPE):  # types 1 to 5
    # Interpolate color: red (1) -> orange (3) -> yellow (5)
    if i == 1:
        color = QColor(255, 0, 0)      # Red
    elif i == 3:
        color = QColor(255, 165, 0)    # Orange
    elif i == 4:
        color = QColor(255, 255, 0)    # Yellow
    else:
        if i < 3:
            r = 255
            g = int(165 * (i-1)/2)
            b = 0
        else:
            r = 255
            g = 165 + int(90 * (i-3)/2)
            b = 0
        color = QColor(r, g, b)
    # Create a line symbol for this category
    symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
    symbol.setColor(color)
    # Optionally, set line width or style if needed
    symbol.setWidth(2)
    category = QgsRendererCategory(i, symbol, str(i))
    categories.append(category)

# Create and set the categorized renderer
renderer = QgsCategorizedSymbolRenderer("type", categories)
xyd.setRenderer(renderer)
xyd.triggerRepaint()


xyd.setName('Interface')


##
# Add point layer to project
layer.setName('Points from csv')
QgsProject.instance().addMapLayer(layer)
print("Memory layer created and added to QGIS!")


## add google satellite (and move it to the bottom)


# Add Google Satellite XYZ layer
uri = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0' #"type=xyz&url=https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&zmax=21"
layer = QgsRasterLayer(uri, "OSM", "wms")

if not layer.isValid():
    print("Google Satellite layer failed to load!")
else:
    project.addMapLayer(layer, False)
    # Optionally move to bottom if needed
    root = project.layerTreeRoot()
    root.insertChildNode(-1, QgsLayerTreeLayer(layer))
