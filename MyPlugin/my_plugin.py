from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (QAction, QMessageBox, QDialog, QVBoxLayout,
                                 QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
                                 QCheckBox, QPushButton, QComboBox, QFileDialog,
                                 QDialogButtonBox)
from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsProject)
from PyQt5.QtCore import QVariant
import os
import sys
import pandas as pd
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer

import random
# ---------------------------
# Parameter Dialog Definition
# ---------------------------
class ParameterDialog(QDialog):
    def __init__(self, parent=None):
        super(ParameterDialog, self).__init__(parent)
        self.setWindowTitle("Enter Parameters")
        self.layout = QVBoxLayout()
        self.formLayout = QFormLayout()

        # INPUT_FOLDER (with browse button)
        self.inputFolderEdit = QLineEdit()
        browseButton = QPushButton("Browse...")
        browseButton.clicked.connect(self.browse_folder)
        self.formLayout.addRow("Input Folder:", self.inputFolderEdit)
        self.formLayout.addRow("", browseButton)

        # option (combobox)
        self.optionCombo = QComboBox()
        self.optionCombo.addItems(["altorisco", "todos"])
        self.formLayout.addRow("Option:", self.optionCombo)

        # D and d
        self.dSpin = QSpinBox()
        self.dSpin.setRange(0, 1000000)
        self.dSpin.setValue(500)  # D = 500
        self.formLayout.addRow("D (Maximum distance):", self.dSpin)

        self.dThresholdSpin = QSpinBox()
        self.dThresholdSpin.setRange(0, 1000000)
        self.dThresholdSpin.setValue(600)  # d = 600
        self.formLayout.addRow("d (Distance threshold):", self.dThresholdSpin)

        # K and KF
        self.KSpin = QSpinBox()
        self.KSpin.setRange(1, 100)
        self.KSpin.setValue(6)
        self.formLayout.addRow("K (flammable neighbors):", self.KSpin)

        self.KFSpin = QSpinBox()
        self.KFSpin.setRange(1, 100)
        self.KFSpin.setValue(5)
        self.formLayout.addRow("KF (urban neighbors):", self.KFSpin)

        # limiar and limiartheta
        self.limiarDoubleSpin = QDoubleSpinBox()
        self.limiarDoubleSpin.setRange(0, 100)
        self.limiarDoubleSpin.setValue(1.05)
        self.formLayout.addRow("limiar (threshold):", self.limiarDoubleSpin)

        self.limiarthetaSpin = QSpinBox()
        self.limiarthetaSpin.setRange(0, 360)
        self.limiarthetaSpin.setValue(60)
        self.formLayout.addRow("limiartheta (largest angle):", self.limiarthetaSpin)

        # MAXDIST
        self.MAXDISTSpin = QSpinBox()
        self.MAXDISTSpin.setRange(0, 1000000)
        self.MAXDISTSpin.setValue(0)
        self.formLayout.addRow("MAXDIST:", self.MAXDISTSpin)

        # Booleans: CREATE_INTERFACE, TESTIDX, DRAWSEGMENTS, DRAWPOINTS, read, Main_Algo, Select, Save
        self.createInterfaceCheck = QCheckBox()
        self.createInterfaceCheck.setChecked(True)
        self.formLayout.addRow("CREATE_INTERFACE:", self.createInterfaceCheck)

        self.TESTIDXCheck = QCheckBox()
        self.TESTIDXCheck.setChecked(True)
        self.formLayout.addRow("TESTIDX:", self.TESTIDXCheck)

        self.DRAWSEGMENTSCheck = QCheckBox()
        self.DRAWSEGMENTSCheck.setChecked(True)
        self.formLayout.addRow("DRAWSEGMENTS:", self.DRAWSEGMENTSCheck)

        self.DRAWPOINTSCheck = QCheckBox()
        self.DRAWPOINTSCheck.setChecked(True)
        self.formLayout.addRow("DRAWPOINTS:", self.DRAWPOINTSCheck)

        self.readCheck = QCheckBox()
        self.readCheck.setChecked(True)
        self.formLayout.addRow("read:", self.readCheck)

        self.MainAlgoCheck = QCheckBox()
        self.MainAlgoCheck.setChecked(True)
        self.formLayout.addRow("Main_Algo:", self.MainAlgoCheck)

        self.SelectCheck = QCheckBox()
        self.SelectCheck.setChecked(True)
        self.formLayout.addRow("Select:", self.SelectCheck)

        self.SaveCheck = QCheckBox()
        self.SaveCheck.setChecked(True)
        self.formLayout.addRow("Save:", self.SaveCheck)

        # Additional parameters: tolerance, bigN, smallN, POSVALUE, NEGVALUE, etc.
        self.toleranceSpin = QSpinBox()
        self.toleranceSpin.setRange(0, 10000)
        self.toleranceSpin.setValue(3)
        self.formLayout.addRow("tolerance:", self.toleranceSpin)

        self.bigNSpin = QSpinBox()
        self.bigNSpin.setRange(0, 1000000000)
        self.bigNSpin.setValue(10**6)
        self.formLayout.addRow("bigN:", self.bigNSpin)

        self.smallNDoubleSpin = QDoubleSpinBox()
        self.smallNDoubleSpin.setDecimals(10)
        self.smallNDoubleSpin.setRange(0, 1)
        self.smallNDoubleSpin.setValue(10**-6)
        self.formLayout.addRow("smallN:", self.smallNDoubleSpin)

        self.POSVALUESpin = QSpinBox()
        self.POSVALUESpin.setRange(0, 1000000)
        self.POSVALUESpin.setValue(9999)
        self.formLayout.addRow("POSVALUE:", self.POSVALUESpin)

        self.NEGVALUESpin = QSpinBox()
        self.NEGVALUESpin.setRange(-1000000, 0)
        self.NEGVALUESpin.setValue(-1)
        self.formLayout.addRow("NEGVALUE:", self.NEGVALUESpin)
        # === Add new fields for x0 and y0 ===
        self.x0DoubleSpin = QDoubleSpinBox()
        self.x0DoubleSpin.setRange(-1e9, 1e9)
        self.x0DoubleSpin.setDecimals(6)
        self.x0DoubleSpin.setValue(-98407.00)  # set a default value if desired
        self.formLayout.addRow("x0:", self.x0DoubleSpin)

        self.y0DoubleSpin = QDoubleSpinBox()
        self.y0DoubleSpin.setRange(-1e9, 1e9)
        self.y0DoubleSpin.setDecimals(6)
        self.y0DoubleSpin.setValue(-102297.80)  # set a default value if desired
        self.formLayout.addRow("y0:", self.y0DoubleSpin)
        # Urban attributes: ADDVAR and NEWVAR, ADDVAR2 and NEWVAR2
        self.ADDVARCheck = QCheckBox()
        self.ADDVARCheck.setChecked(True)
        self.formLayout.addRow("ADDVAR:", self.ADDVARCheck)

        self.NEWVAREdit = QLineEdit()
        self.NEWVAREdit.setText("fid_1")
        self.formLayout.addRow("NEWVAR:", self.NEWVAREdit)

        self.ADDVAR2Check = QCheckBox()
        self.ADDVAR2Check.setChecked(False)
        self.formLayout.addRow("ADDVAR2:", self.ADDVAR2Check)

        self.NEWVAR2Edit = QLineEdit()
        self.NEWVAR2Edit.setText("CorePC")
        self.formLayout.addRow("NEWVAR2:", self.NEWVAR2Edit)

        # Flammable attributes: ADDFLAMVAR and NEWFLAMVAR, ADDFLAMVAR2 and NEWFLAMVAR2
        self.ADDFLAMVARCheck = QCheckBox()
        self.ADDFLAMVARCheck.setChecked(True)
        self.formLayout.addRow("ADDFLAMVAR:", self.ADDFLAMVARCheck)

        self.NEWFLAMVAREdit = QLineEdit()
        self.NEWFLAMVAREdit.setText("idflam")
        self.formLayout.addRow("NEWFLAMVAR:", self.NEWFLAMVAREdit)

        self.ADDFLAMVAR2Check = QCheckBox()
        self.ADDFLAMVAR2Check.setChecked(False)
        self.formLayout.addRow("ADDFLAMVAR2:", self.ADDFLAMVAR2Check)

        self.NEWFLAMVAR2Edit = QLineEdit()
        self.NEWFLAMVAR2Edit.setText("FuelRisk")
        self.formLayout.addRow("NEWFLAMVAR2:", self.NEWFLAMVAR2Edit)

        self.layout.addLayout(self.formLayout)

        # Standard dialog buttons (OK, Cancel)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(buttonBox)
        self.setLayout(self.layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder", "")
        if folder:
            self.inputFolderEdit.setText(folder)

    def getValues(self):
        return {
            "INPUT_FOLDER": self.inputFolderEdit.text(),
            "option": self.optionCombo.currentText(),
            "D": self.dSpin.value(),
            "d": self.dThresholdSpin.value(),
            "K": self.KSpin.value(),
            "KF": self.KFSpin.value(),
            "limiar": self.limiarDoubleSpin.value(),
            "limiartheta": self.limiarthetaSpin.value(),
            "MAXDIST": self.MAXDISTSpin.value(),
            "CREATE_INTERFACE": self.createInterfaceCheck.isChecked(),
            "TESTIDX": self.TESTIDXCheck.isChecked(),
            "DRAWSEGMENTS": self.DRAWSEGMENTSCheck.isChecked(),
            "DRAWPOINTS": self.DRAWPOINTSCheck.isChecked(),
            "read": self.readCheck.isChecked(),
            "Main_Algo": self.MainAlgoCheck.isChecked(),
            "Select": self.SelectCheck.isChecked(),
            "Save": self.SaveCheck.isChecked(),
            "tolerance": self.toleranceSpin.value(),
            "bigN": self.bigNSpin.value(),
            "smallN": self.smallNDoubleSpin.value(),
            "POSVALUE": self.POSVALUESpin.value(),
            "NEGVALUE": self.NEGVALUESpin.value(),
            "ADDVAR": self.ADDVARCheck.isChecked(),
            "NEWVAR": self.NEWVAREdit.text(),
            "ADDVAR2": self.ADDVAR2Check.isChecked(),
            "NEWVAR2": self.NEWVAR2Edit.text(),
            "ADDFLAMVAR": self.ADDFLAMVARCheck.isChecked(),
            "NEWFLAMVAR": self.NEWFLAMVAREdit.text(),
            "ADDFLAMVAR2": self.ADDFLAMVAR2Check.isChecked(),
            "NEWFLAMVAR2": self.NEWFLAMVAR2Edit.text(),
            "x0": self.x0DoubleSpin.value(),
            "y0": self.y0DoubleSpin.value(),
        }

# ---------------------------
# Helper Function: Load datatable as a point layer
# ---------------------------
def load_datatable_as_point_layer(dt_frame, layer_name, crs_epsg=4326, x_col="x", y_col="y"):
    """
    Convert a datatable.Frame (or Pandas DataFrame) with X/Y columns into
    an in-memory point layer and add it to QGIS.

    :param dt_frame: datatable.Frame or Pandas DataFrame
    :param layer_name: name of the layer in QGIS
    :param crs_epsg: EPSG code for the coordinate reference system (int)
    :param x_col: column name for the X coordinate
    :param y_col: column name for the Y coordinate
    :return: reference to the newly created QgsVectorLayer
    """
    try:
        df = dt_frame.to_pandas()
    except AttributeError:
        # If it’s already a DataFrame, use it directly
        df = dt_frame

    # Create a memory layer for points (use the specified EPSG)
    uri = f"Point?crs=EPSG:{crs_epsg}"
    mem_layer = QgsVectorLayer(uri, layer_name, "memory")
    pr = mem_layer.dataProvider()

    # Define fields for all columns except X and Y
    fields = []
    for col in df.columns:
        if col not in [x_col, y_col]:
            # For simplicity, treat all as float/double
            fields.append(QgsField(col, QVariant.Double))
    pr.addAttributes(fields)
    mem_layer.updateFields()

    # Add features (one per row)
    features = []
    all_cols = list(df.columns)
    for idx, row in df.iterrows():
        x_val = row[x_col]
        y_val = row[y_col]
        feat = QgsFeature()
        # Geometry from (x, y)
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x_val), float(y_val))))

        # Attributes
        attr_vals = []
        for col in all_cols:
            if col not in [x_col, y_col]:
                try:
                    val = float(row[col])
                except:
                    val = None
                attr_vals.append(val)
        feat.setAttributes(attr_vals)
        features.append(feat)

    pr.addFeatures(features)
    mem_layer.updateExtents()
    mem_layer.updateFields()

    # Add to QGIS project
    QgsProject.instance().addMapLayer(mem_layer)
    return mem_layer

# ---------------------------
# Helper Function: Create vector layer from GeoPandas DataFrame
# ---------------------------
def create_vector_layer_from_gdf(gdf, layer_name, crs):
    if gdf.empty:
        return None
    # Determine geometry type based on the first feature
    geom_type = gdf.geometry.geom_type.iloc[0]
    if geom_type == "Point":
        layer_type = "Point"
    elif geom_type == "LineString":
        layer_type = "LineString"
    elif geom_type in ["Polygon", "MultiPolygon"]:
        layer_type = "Polygon"
    else:
        layer_type = "Unknown"
    layer = QgsVectorLayer(f"{layer_type}?crs={crs}", layer_name, "memory")
    pr = layer.dataProvider()
    fields = []
    for col in gdf.columns:
        if col == gdf.geometry.name:
            continue
        if pd.api.types.is_numeric_dtype(gdf[col]):
            fields.append(QgsField(col, QVariant.Double))
        else:
            fields.append(QgsField(col, QVariant.String))
    pr.addAttributes(fields)
    layer.updateFields()
    features = []
    for idx, row in gdf.iterrows():
        feat = QgsFeature()
        geom_wkt = row[gdf.geometry.name].wkt
        feat.setGeometry(QgsGeometry.fromWkt(geom_wkt))
        feat.setAttributes([row[field.name()] for field in fields])
        features.append(feat)
    pr.addFeatures(features)
    layer.updateExtents()
    return layer

# ---------------------------
# Main Plugin Class
# ---------------------------
class MyPlugin:
    def __init__(self, iface):
        """Constructor.
        :param iface: A QGIS interface instance.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&My Plugin')

    def tr(self, message):
        return QCoreApplication.translate('MyPlugin', message)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.action = QAction(self.tr(u'Run My Plugin'), self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)
        self.actions.append(self.action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        # Prompt the user to enter parameter values
        dialog = ParameterDialog()
        if dialog.exec_():
            params = dialog.getValues()

            # Assign parameter values from the dialog
            INPUT_FOLDER     = params["INPUT_FOLDER"]
            option           = params["option"]
            D                = params["D"]
            d                = params["d"]
            K                = params["K"]
            KF               = params["KF"]
            limiar           = params["limiar"]
            limiartheta      = params["limiartheta"]
            MAXDIST          = params["MAXDIST"]
            CREATE_INTERFACE = params["CREATE_INTERFACE"]
            TESTIDX          = params["TESTIDX"]
            DRAWSEGMENTS     = params["DRAWSEGMENTS"]
            DRAWPOINTS       = params["DRAWPOINTS"]
            read             = params["read"]
            Main_Algo        = params["Main_Algo"]
            Select           = params["Select"]
            Save             = params["Save"]
            tolerance        = params["tolerance"]
            bigN             = params["bigN"]
            smallN           = params["smallN"]
            POSVALUE         = params["POSVALUE"]
            NEGVALUE         = params["NEGVALUE"]
            ADDVAR           = params["ADDVAR"]
            NEWVAR           = params["NEWVAR"]
            ADDVAR2          = params["ADDVAR2"]
            NEWVAR2          = params["NEWVAR2"]
            ADDFLAMVAR       = params["ADDFLAMVAR"]
            NEWFLAMVAR       = params["NEWFLAMVAR"]
            ADDFLAMVAR2      = params["ADDFLAMVAR2"]
            NEWFLAMVAR2      = params["NEWFLAMVAR2"]
            x0               = params["x0"]
            y0               = params["y0"]
            ##############################################
            #    Libraries       #  
            ##############################################
            import os
            import pandas as pd
            import geopandas as gpd
            import numpy as np 
            import glob
            import matplotlib.pyplot as plt
            import pickle
            import sys
            import datatable as dt 

            ############################################################################################
            #    This is related to get functions from Functions directory     #  
            ############################################################################################
            # Get the absolute path of the parent directory (Interface_Github)
            parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # Add the parent directory to sys.path
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            ##############################################
            #    Files call     #  
            ##############################################
            from . import plugin_imports
            create_bounding_box = plugin_imports.create_bounding_box
            promote_to_multipolygon=plugin_imports.promote_to_multipolygon
            process_flammables=plugin_imports.process_flammables 
            extract_vertices=plugin_imports.extract_vertices    
            clean_and_reindex=plugin_imports.clean_and_reindex   
            nearest_indices=plugin_imports.nearest_indices
            get_neighbors=plugin_imports.get_neighbors
            idxneigh=plugin_imports.idxneigh  
            adjust_coordinates=plugin_imports.adjust_coordinates
            decision=plugin_imports.decision
            azimuthVF=plugin_imports.azimuthVF
            ftype=plugin_imports.ftype
            ##############################################
            #    Set directory     #
            ##############################################
            INPUT_FOLDER = "C:\\Users\\aziza\\Desktop\\Interface_Github\\Data"  # Data Folder
            
            option = "altorisco"  # Choose between "altorisco" (high-risk) or "todos" (all areas)
            
            if option == "altorisco":
                inputFlamm = "high_risk_sintra.shp"  # High-risk combustible areas
            elif option == "todos":
                inputFlamm = "all_risk_sintra.shp"  # All combustible areas 
            
            urban_file = "urban_sintra.shp"  # Buffered Urban area file
            
            if option == "altorisco":
                extraname = "8set19GLisboaAltoRisco"  
            elif option == "todos":
                extraname = "8set19GLisboaTodos"  
            
            flammable_path = os.path.join(INPUT_FOLDER, inputFlamm)  # Full path to flammable file
            urban_path = os.path.join(INPUT_FOLDER, urban_file)  # Full path to urban file
            
            OUTPUT_FOLDER = "C:\\Users\\aziza\\Desktop\\Interface_Github\\Output"  
            
            ##############################################
            #    Test specific location     #
            ##############################################
            if TESTIDX:
                K = K
                KS = list(range(1, K+1))
                KF = KF
                KFS = list(range(1, KF+1))
                extraname = f"test-{extraname}" 
            
            coords1 = {'x': [-9.27950], 'y': [38.74991]} 
            gdf1 = gpd.GeoDataFrame(pd.DataFrame(coords1), geometry=gpd.points_from_xy(coords1['x'], coords1['y']), crs='EPSG:4326')  
            coords2 = {'x': [-9.27794], 'y': [38.74570]} 
            gdf2 = gpd.GeoDataFrame(pd.DataFrame(coords2), geometry=gpd.points_from_xy(coords2['x'], coords2['y']), crs='EPSG:4326') 
            gdf2_transformed = gdf2.to_crs('EPSG:3763') 
            x0y0_coords = gdf2_transformed.geometry.apply(lambda geom: (geom.x, geom.y)).tolist()[0] 
            
            ##############################################
            #    Test Point x0y0     #
            ##############################################
            x0y0 = pd.DataFrame([{'X': -98407.00, 'Y': -102297.80}]) #it s correct (d=500,K = 5,KF=4)
            
            
            ##############################################
            #    Bounding Box    # 
            ##############################################
            x0 = x0y0["X"].values[0]  
            y0 = x0y0["Y"].values[0]  
            BOX = create_bounding_box(x0,y0, d) # Creates a bounding box centered at (x0, y0) with distance 'd'
            
            
            ##############################################
            #    Reading Part #
            ##############################################
            if read:
                if CREATE_INTERFACE or TESTIDX:
                    # Process Flammable Data
                    flam = gpd.read_file(flammable_path) 
                    flam = promote_to_multipolygon(flam)  
                    if TESTIDX:
                        flam =process_flammables(flam, BOX)
                    flam["idflam"] = range(1, len(flam) + 1)
                    xy_flam = extract_vertices(flam) 
                    if 'L3' not in xy_flam.columns or xy_flam['L3'].max() != len(flam):
                        raise ValueError("L3 is not properly indexed")
                    idx_L1 = xy_flam['L1']
                    idx_L2 = xy_flam['L2']
                    M = 10 ** (1 + np.ceil(np.log10(idx_L2.max())).astype(int))
                    Q = 10 ** (1 + np.ceil(np.log10(idx_L1.max())).astype(int))
                    idx_feat_flam = xy_flam['L3']
                    idx_part_flam = M * Q * idx_feat_flam + M * idx_L1 + idx_L2
                    mat_flam = pd.DataFrame({
                        'x': np.round(xy_flam['x']),
                        'y': np.round(xy_flam['y']),
                        'idx_feat_flam': idx_feat_flam,
                        'idx_part_flam': idx_part_flam.round()
                    })
            
                    # Handle additional variables
                    if ADDFLAMVAR and not ADDFLAMVAR2:
                        flamtable  = pd.DataFrame({
                            'idx_feat_flam': range(1, len(flam) + 1),
                            'newflamvar': flam[NEWFLAMVAR]
                        })
                    elif ADDFLAMVAR2:
                        flamtable  = pd.DataFrame({
                            'idx_feat_flam': range(1, len(flam) + 1),
                            'newflamvar': flam[NEWFLAMVAR],
                            'newflamvar2': flam[NEWFLAMVAR2]
                        })
                    mat_flam = clean_and_reindex(mat_flam,"idx_part_flam","idx_vert_flam") # Remove duplicates
                    # Process Urban Data 
                    urb = gpd.read_file(urban_path)
                    urb = urb.to_crs(flam.crs)
                    if TESTIDX:
                        urb = process_flammables(urb,BOX)
                    urb['idurb'] = range(1, len(urb) + 1)   
                    xy_urb = extract_vertices(urb)
                    if 'L3' not in xy_urb.columns or xy_urb['L3'].max() != len(urb):
                        raise ValueError("L3 is not properly indexed")
                    idx_L1 = xy_urb['L1']
                    idx_L2 = xy_urb['L2']
                    M = 10 ** (1 + np.ceil(np.log10(idx_L2.max())).astype(int))
                    Q = 10 ** (1 + np.ceil(np.log10(idx_L1.max())).astype(int))
                    idx_feat_urb = xy_urb['L3']
                    idx_part_urb = M * Q * idx_feat_urb + M * idx_L1 + idx_L2
                    mat_urb = pd.DataFrame({
                        'x': np.round(xy_urb['x']),
                        'y': np.round(xy_urb['y']),
                        'idx_feat_urb': idx_feat_urb,
                        'idx_part_urb': idx_part_urb.round()
                    })
                    if ADDVAR and not ADDVAR2:
                        newtable = pd.DataFrame({
                            'idx_feat_urb': range(1, len(urb) + 1),
                            'newvar': urb[NEWVAR]
                        })
                    elif ADDVAR2:
                        newtable = pd.DataFrame({
                            'idx_feat_urb': range(1, len(urb) + 1),
                            'newvar': urb[NEWVAR],
                            'newvar2': urb[NEWVAR2]
                        })
                    mat_urb = clean_and_reindex(mat_urb,"idx_part_urb","idx_vert_urb") # Remove duplicates
            
                    mat_urb_dt = dt.Frame(mat_urb)
                    mat_flam_dt = dt.Frame(mat_flam)
                    
                    # search nearest flammable neighbor 
                    idxUF_idx=nearest_indices(mat_urb_dt,mat_flam_dt,k=1)
                    mat_flam_dt['idx_vert_urb'] = idxUF_idx # urban vertices of flam vertices
                    idxFU_idx=nearest_indices(mat_flam_dt,mat_urb_dt,k=1)
                    mat_urb_dt['idx_vert_flam'] = idxFU_idx # Flammable neighbors of urban vertices
            if read:
                distances_squared = (mat_urb_dt["x"].to_numpy() - x0)**2 + (mat_urb_dt["y"].to_numpy() - y0)**2
                id0 = np.argmin(distances_squared) 
                # determining the K Flam neighbors up to distance D meters from each urban neighbor
                # Calculating the distance from each vertice of the urban polygons to each vertice within D meters  of the flammable polygons
                knn_idx,knn_dists=nearest_indices(mat_flam_dt,mat_urb_dt,k=K, return_distance=True) # neighbors urban X Flam
                FICHNAME= f"interface_K{K}_KF{KF}_limiar{round(limiar * 100)}_maxdist{MAXDIST}-maxtheta{limiartheta}-{extraname}.pickle"
                fichs = glob.glob(os.path.join(OUTPUT_FOLDER, f"{FICHNAME}.pickle"))
            ##############################################
            # Main Algorithm
            ##############################################
            if Main_Algo:
                mat_urb_df = mat_urb_dt.to_pandas()
                mat_flam_df = mat_flam_dt.to_pandas()
                if CREATE_INTERFACE or TESTIDX or len(fichs) == 0:
                    not_interface = np.full(len(mat_urb_df), True)  
                    dF = np.full(len(mat_urb_df), POSVALUE)
                    dFplus = np.full(len(mat_urb_df), NEGVALUE)
                    azF = np.full(len(mat_urb_df), NEGVALUE)
                    azFplus = np.full(len(mat_urb_df), NEGVALUE)
                    iF = np.full(len(mat_urb_df), NEGVALUE)
                    kvw_idx, kvw_dists = nearest_indices(mat_urb_dt, k=KF, return_distance=True)
                    xV = mat_urb_df['x']
                    yV = mat_urb_df['y']
                    k = 1
                    for k in KS:
                        threetimesprotected = np.full(len(mat_urb_df), True)
                        idxF = knn_idx.iloc[:, k-1]
                        xF, yF, xFF, yFF, xFFF, yFFF, idxfeatF = get_neighbors(mat_df=mat_flam_df, idx=idxF, idxneigh_func=idxneigh, in_type="flam", x_col='x', y_col='y', feat_col='idx_feat_flam')
                        xFF, yFF = adjust_coordinates(xF, yF, xFF, yFF, xV, yV)
                        xFFF, yFFF = adjust_coordinates(xF, yF, xFFF, yFFF, xV, yV)
                        xFback = xF
                        yFback = yF
                        idxFviz = 3
                        for idxFviz in range(1, 4):
                            protected = np.full(len(mat_urb_df), False, dtype=bool)
                            if idxFviz == 2:
                                xF = xFF
                                yF = yFF
                            elif idxFviz == 3:
                                xF = xFFF
                                yF = yFFF
                            if not TESTIDX:
                                print(f"iteration {k} among F-neighbors and idxFviz={idxFviz} in 3")
                            xF = np.where(np.isnan(xF), bigN, xF)
                            yF = np.where(np.isnan(yF), bigN, yF)
                            idxfeatF = np.where(np.isnan(idxfeatF), NEGVALUE, idxfeatF)
                            for j in KFS:
                                if not TESTIDX and j % 10 == 0:
                                    print(f"GROUP1: iteration {j} among urban neighbors of V")
                                d2VW = kvw_dists.iloc[:, j-1] ** 2
                                xW1, yW1, xWW1, yWW1, xWWW1, yWWW1, _ = get_neighbors(mat_df=mat_urb_df, idx=kvw_idx.iloc[:, j-1], idxneigh_func=idxneigh, in_type="urb", x_col='x', y_col='y', feat_col='idx_feat_urb')
                                d2WF = (xW1 - xF) ** 2 + (yW1 - yF) ** 2
                                isprotected1 = decision(D, limiar, limiartheta, xV, yV, xF, yF, xW1, yW1, xWW1, yWW1, xWWW1, yWWW1, verbose=False, log_file="decision_table1.csv")
                                protected1 = protected | isprotected1
                            query = dt.Frame(np.column_stack((xF, yF)), names=['x', 'y'])
                            kfw_idx, kfw_dists = nearest_indices(mat_urb_dt, query, k=KF, return_distance=True)
                            for j in KFS:
                                if not TESTIDX and j % 10 == 0:
                                    print(f"GROUP2: iteration {j} among urban neighbors of Flam neighbors of V")
                                d2WF = kfw_dists.iloc[:, j-1] ** 2
                                xW2, yW2, xWW2, yWW2, xWWW2, yWWW2, _ = get_neighbors(mat_df=mat_urb_df, idx=kfw_idx.iloc[:, j-1], idxneigh_func=idxneigh, in_type="urb", x_col='x', y_col='y', feat_col='idx_feat_urb')
                                d2VW = (xW2 - xV) ** 2 + (yW2 - yV) ** 2
                                isprotected2 = decision(D, limiar, limiartheta, xV, yV, xF, yF, xW2, yW2, xWW2, yWW2, xWWW2, yWWW2, verbose=False, log_file="decision_table2.csv")
                                protected2 = protected | isprotected2
                            protected = protected1 | protected2
                            d2VFcurrent = (xV - xF)**2 + (yV - yF)**2
                            azVFcurrent = azimuthVF(xV=xV, yV=yV, xF=xF, yF=yF)
                            idxVFcurrent = idxfeatF
                            if idxFviz == 1:
                                d2VF = d2VFcurrent
                                azVF = azVFcurrent
                                idxVF = idxVFcurrent
                            elif idxFviz > 1:
                                idxVF = (d2VFcurrent < d2VF) * idxVFcurrent + (d2VFcurrent >= d2VF) * idxVF
                                azVF = (d2VFcurrent < d2VF) * azVFcurrent + (d2VFcurrent >= d2VF) * azVF
                                d2VF = (d2VFcurrent < d2VF) * d2VFcurrent + (d2VFcurrent >= d2VF) * d2VF
                            threetimesprotected = threetimesprotected & protected
                            iF = (threetimesprotected * iF) + (~threetimesprotected * ((d2VF < dF**2) * idxVF + (d2VF >= dF**2) * iF))
                            azF = (threetimesprotected * azF) + (~threetimesprotected * ((d2VF < dF**2) * azVF + (d2VF >= dF**2) * azF))
                            dF = (threetimesprotected * dF) + (~threetimesprotected * ((d2VF < dF**2) * np.sqrt(d2VF) + (d2VF >= dF**2) * dF))
                            not_interface = not_interface & threetimesprotected
                    interface = ~not_interface
                    interface[pd.isna(knn_idx.iloc[:, 0])] = False
                    if not TESTIDX:
                        save_path = os.path.join(OUTPUT_FOLDER, f"{FICHNAME}.pkl")
                        with open(save_path, 'wb') as f:
                            pickle.dump([interface, dF, azF, iF, azFplus, dFplus], f)
                if not CREATE_INTERFACE and not TESTIDX and len(fichs) > 0:
                    with open(fichs[0], 'rb') as f:
                        data = pickle.load(f)
            ##############################################
            # Select Interface and Add Features
            ##############################################
            if Select:
                # Ensure crs_code is defined for later use
                try:
                    crs_code
                except NameError:
                    if flam.crs is not None:
                        crs_code = flam.crs.to_epsg()
                    else:
                        crs_code = 4326
                xyd = dt.Frame({
                    'x': mat_urb_df['x'].to_list(),  
                    'y': mat_urb_df['y'].to_list(),  
                    'idx_part_u': mat_urb_df['idx_part_urb'].to_list(),  
                    'idx_feat_u': mat_urb_df['idx_feat_urb'].to_list(), 
                    'idx_vert_u': mat_urb_df['idx_vert_urb'].to_list(),  
                    'vert_type': ftype(dF, D).tolist(),  
                    'idx_feat_f': mat_flam_df.loc[idxF, 'idx_feat_flam'].values,  
                    'dist_feat_f': knn_dists.iloc[:, 0].to_list(),  
                    'd': dF.tolist(),  
                    'az': azF.tolist(),  
                    'iF': iF.tolist(),  
                    'interface': interface.astype(int).tolist()
                })
                xyd[dt.f.d == POSVALUE, 'd'] = NEGVALUE
                xyd[dt.isna(dt.f.iF), 'iF'] = NEGVALUE
                xydL = xyd[2:, :]
                xydR = xyd[:-2, :]
                xydL.names = [f"{name}_L" for name in xyd.names]
                xydR.names = [f"{name}_R" for name in xyd.names]
                xyd_middle = xyd[1:-1, :]
                xydDT = dt.cbind(xyd_middle, xydL, xydR)
                xydDT = xydDT[:, :, dt.sort(dt.f.idx_vert_u)]
                xydDT[:, dt.update(lengthL=np.sqrt((xydDT['x_L'].to_numpy() - xydDT['x'].to_numpy())**2 + 
                                                  (xydDT['y_L'].to_numpy() - xydDT['y'].to_numpy())**2))]
                xydDT[:, dt.update(lengthR=np.sqrt((xydDT['x_R'].to_numpy() - xydDT['x'].to_numpy())**2 + 
                                                  (xydDT['y_R'].to_numpy() - xydDT['y'].to_numpy())**2))]
                xydDT[dt.f.idx_part_u != dt.f.idx_part_u_L, dt.update(lengthL=NEGVALUE)]
                xydDT[dt.f.idx_part_u != dt.f.idx_part_u_R, dt.update(lengthR=NEGVALUE)]
                xydDT[:, dt.update(azimuthL=azimuthVF(xydDT['x'].to_numpy(), 
                                                     xydDT['y'].to_numpy(), 
                                                     xydDT['x_L'].to_numpy(), 
                                                     xydDT['y_L'].to_numpy()))]
                xydDT[:, dt.update(azimuthR=azimuthVF(xydDT['x'].to_numpy(), 
                                                     xydDT['y'].to_numpy(), 
                                                     xydDT['x_R'].to_numpy(), 
                                                     xydDT['y_R'].to_numpy()))]
                xydDT[dt.f.idx_part_u != dt.f.idx_part_u_L, dt.update(azimuthL=NEGVALUE)]
                xydDT[dt.f.idx_part_u != dt.f.idx_part_u_R, dt.update(azimuthR=NEGVALUE)]
                xydDT[:, dt.update(linkR=(dt.f.interface | dt.f.interface_R) & 
                                     (dt.f.idx_part_u == dt.f.idx_part_u_R) & 
                                     (dt.math.abs(dt.f.idx_vert_u - dt.f.idx_vert_u_R) <= 1))]
                xydDT[:, dt.update(linkL=(dt.f.interface | dt.f.interface_L) & 
                                     (dt.f.idx_part_u == dt.f.idx_part_u_L) & 
                                     (dt.math.abs(dt.f.idx_vert_u - dt.f.idx_vert_u_L) <= 1))]
                xydDT[:, dt.update(steplinkL=dt.shift(dt.f.linkL, -1) - dt.f.linkL)]
                xydDT[:, dt.update(segmentL=dt.cumsum((dt.f.steplinkL >= 0) * dt.f.steplinkL))]
                xydDT[:, dt.update(steplinkR=dt.f.linkR - dt.shift(dt.f.linkR))]
                xydDT[:, dt.update(segmentR=1 + dt.cumsum((dt.f.steplinkR <= 0) * dt.math.abs(dt.f.steplinkR)))]
                xydDT[(dt.f.interface == False) & (dt.f.interface_R == False), dt.update(segmentR=NEGVALUE)]
                xydDT[(dt.f.interface == False) & (dt.f.interface_L == False), dt.update(segmentL=NEGVALUE)]
                xydDT[:, dt.update(azsegmentL=NEGVALUE)]
                colnames_xydDT = xydDT.names
                VARS = ['idx_feat_u', 'x', 'y', 'idx_part_u', 'idx_vert_u', 'vert_type', 'idx_feat_f', 'dist_feat_f', 'd', 'az', 'iF', 'interface',
                        'linkL', 'linkR', 'lengthL', 'lengthR', 'segmentL', 'segmentR', 'azimuthL', 'azimuthR']
                xydDT = xydDT[:, VARS]
                newtable_dt = dt.Frame(newtable)
                flamtable_dt = dt.Frame(flamtable)
                newtable_dt.names = ['idx_feat_u' if name == 'idx_feat_urb' else name for name in newtable_dt.names]
                flamtable_dt.names = ['idx_feat_f' if name == 'idx_feat_flam' else name for name in flamtable_dt.names]
                if ADDVAR:
                    newtable_dt.key = 'idx_feat_u'
                    xydDT = xydDT[:, :, dt.join(newtable_dt)]
                if ADDFLAMVAR:
                    flamtable_dt.key = 'idx_feat_f'
                    xydDT = xydDT[:, :, dt.join(flamtable_dt)]
                interface_pts = xydDT[:, :, dt.sort(dt.f.idx_vert_u)].copy()
                interface_pts[:, ['idx_part_u', 'idx_vert_u']] = None
                if ADDVAR:
                    interface_pts[NEWVAR] = interface_pts['newvar']
                    interface_pts[:, 'newvar'] = None  
                if ADDVAR2:
                    interface_pts[NEWVAR2] = interface_pts['newvar2']
                    interface_pts[:, 'newvar2'] = None  
                if ADDFLAMVAR:
                    interface_pts[NEWFLAMVAR] = interface_pts['newflamvar']
                    interface_pts[:, 'newflamvar'] = None  
                if ADDFLAMVAR2:
                    interface_pts[NEWFLAMVAR2] = interface_pts['newflamvar2']
                    interface_pts[:, 'newflamvar2'] = None  
                OUTNAME = FICHNAME + ".txt"
                if Save:
                    xydDT_df = xydDT.to_pandas()
                    output_path33 = os.path.join(OUTPUT_FOLDER,"xydDT.csv")
                    xydDT_df.to_csv(output_path33, sep=',', index=False)
                # Load xydDT as a point layer in QGIS
                xydDT_df = xydDT.to_pandas()
                xyd_layer = load_datatable_as_point_layer(xydDT_df, "Interface_Points", crs_epsg=crs_code, x_col="x", y_col="y")
                
            # -------------------------------------------------------------
            # Load mat_flam_dt and mat_urb_dt as point layers in QGIS
            # -------------------------------------------------------------
            if flam.crs is not None:
                crs_code = flam.crs.to_epsg()
            else:
                crs_code = 4326
            flam_layer = load_datatable_as_point_layer(
                dt_frame=mat_flam_dt,
                layer_name="Flam_Vertices",
                crs_epsg=crs_code,
                x_col="x",
                y_col="y"
            )
            urb_layer = load_datatable_as_point_layer(
                dt_frame=mat_urb_dt,
                layer_name="Urb_Vertices",
                crs_epsg=crs_code,
                x_col="x",
                y_col="y"
            )
            
            # -------------------------------------------------------------
            # Also load the original GeoPandas layers (flam and urb) as QGIS vector layers
            # -------------------------------------------------------------
            flam_gdf_layer = create_vector_layer_from_gdf(flam, "Flammable Polygons", f"EPSG:{crs_code}")
            urb_gdf_layer = create_vector_layer_from_gdf(urb, "Urban Polygons", f"EPSG:{crs_code}")
            if flam_gdf_layer is not None:
                QgsProject.instance().addMapLayer(flam_gdf_layer)
            if urb_gdf_layer is not None:
                QgsProject.instance().addMapLayer(urb_gdf_layer)
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Opsmos",
                "Flammable & Urban vertex layers, and original polygon layers, added to QGIS."
            )
            