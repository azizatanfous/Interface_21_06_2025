import os
import sys
import random
import pandas as pd
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsMarkerSymbol, QgsSingleSymbolRenderer, QgsVectorLayer
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QAction, QMessageBox, QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QComboBox,
    QFileDialog, QDialogButtonBox
)
from qgis.PyQt.QtGui import QColor  # needed for some versions of QGIS

from qgis.core import (
    QgsFeature, QgsGeometry, QgsVectorLayer, QgsField, QgsSymbol,
    QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsPointXY,
    QgsWkbTypes, QgsProject, QgsRasterLayer, QgsStyle,
    QgsRuleBasedRenderer
)
from qgis.gui import QgsMapToolEmitPoint
import time
from qgis.utils import iface

from .interface_dialogue import ParameterDialog

# ---------------------------
# Helper Function: Load datatable as a point layer
# ---------------------------
def load_datatable_as_point_layer(dt_frame, layer_name, crs_epsg=4326, x_col="x", y_col="y"):
    """
    Convert a datatable.Frame (or Pandas DataFrame) with X/Y columns into
    an in-memory point layer and return it (does NOT add to the project).
    """
    # get a pandas DataFrame
    try:
        df = dt_frame.to_pandas()
    except AttributeError:
        df = dt_frame

    # create memory layer
    uri = f"Point?crs=EPSG:{crs_epsg}"
    mem_layer = QgsVectorLayer(uri, layer_name, "memory")
    pr = mem_layer.dataProvider()

    # add all non-X/Y columns as attributes
    fields = []
    for col in df.columns:
        if col not in (x_col, y_col):
            fields.append(QgsField(col, QVariant.Double))
    pr.addAttributes(fields)
    mem_layer.updateFields()

    # create one feature per row
    feats = []
    for _, row in df.iterrows():
        feat = QgsFeature()
        feat.setGeometry(
            QgsGeometry.fromPointXY(
                QgsPointXY(float(row[x_col]), float(row[y_col]))
            )
        )
        # in-order attribute list
        vals = []
        for fld in fields:
            try:
                vals.append(float(row[fld.name()]))
            except Exception:
                vals.append(None)
        feat.setAttributes(vals)
        feats.append(feat)

    pr.addFeatures(feats)
    mem_layer.updateExtents()
    return mem_layer


# ---------------------------
# Helper Function: Create vector layer from GeoPandas DataFrame
# ---------------------------
def create_vector_layer_from_gdf(gdf, layer_name, crs):
    """
    Turn a GeoPandas GeoDataFrame into an in-memory vector layer
    and return it (does NOT add to the project).
    """
    if gdf.empty:
        return None

    # pick the geometry type
    geom_type = gdf.geometry.geom_type.iloc[0]
    if geom_type == "Point":
        layer_type = "Point"
    elif geom_type == "LineString":
        layer_type = "LineString"
    else:
        layer_type = "Polygon"

    layer = QgsVectorLayer(f"{layer_type}?crs={crs}", layer_name, "memory")
    pr = layer.dataProvider()

    # build attribute fields
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

    # add features
    feats = []
    for _, row in gdf.iterrows():
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromWkt(row[gdf.geometry.name].wkt))
        feat.setAttributes([row[f.name()] for f in fields])
        feats.append(feat)

    pr.addFeatures(feats)
    layer.updateExtents()
    return layer

# ---------------------------
# Main Plugin
# ---------------------------
class MyPlugin:
    def __init__(self, iface):
        """Constructor.
        :param iface: A QGIS interface instance.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = QCoreApplication.translate('MyPlugin', '&My Plugin')

        # prepare our point-picker tool
        self.pointTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.pointTool.canvasClicked.connect(self.onMapClick)  # this now works because onMapClick is inside the class

    def activateMapTool(self):
        """Switch QGIS into point-picker mode, hide dialog for clicking."""
        self.dlg.hide()
        self.iface.mapCanvas().setMapTool(self.pointTool)

    def onMapClick(self, point, button):
        """Handle map click: fill X/Y, restore tools, re-show the same dialog."""
        self.dlg.x0DoubleSpin.setValue(point.x())
        self.dlg.y0DoubleSpin.setValue(point.y())
        self.iface.mapCanvas().unsetMapTool(self.pointTool)
        self.dlg.show()

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
        if not hasattr(self, 'dlg') or self.dlg is None:
            self.dlg = ParameterDialog()
            self.dlg.pickPointBtn.clicked.connect(self.activateMapTool)

        if not self.dlg.exec_():
            return

        remove_reply = QMessageBox.question(
            None,
            self.tr('Remove previous layers'),
            self.tr('Do you want to remove layers from the previous run?'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if remove_reply == QMessageBox.Yes:
            project = QgsProject.instance()
            for layer_name in [
                "Flammable_Polygons", "Urban_Polygons", "OpenStreetMap",
                "Flam_Vertices", "Urb_Vertices", "Interface_Points"
            ]:
                for lyr in [lyr for lyr in project.mapLayers().values() if lyr.name() == layer_name]:
                    project.removeMapLayer(lyr.id())


        params = self.dlg.getValues()
        # General
        INPUT_FOLDER     = params["INPUT_FOLDER"]
        OUTPUT_FOLDER     = params["OUTPUT_FOLDER"]
        option           = params["option"]
        X               = params["x0"]
        Y               = params["y0"]
        d                = params["d_box"]
        K                = params["K"]
        KF               = params["KF"]
        limiar           = params["limiar"]
        limiartheta      = params["limiartheta"]
        MAXDIST          = params["MAXDIST"]

        # Constants & Toggles (tab 3)

        tolerance        = params["tolerance"]
        KDTREE_DIST_UPPERBOUND= params["KDTREE_DIST_UPPERBOUND"]
        bigN             = params["bigN"]
        smallN           = params["smallN"]
        POSVALUE         = params["POSVALUE"]
        NEGVALUE         = params["NEGVALUE"]
        Q                = params["QT"]
        

        ADDVAR           = params["ADDVAR"]
        NEWVAR           = params["NEWVAR"]
        ADDVAR2          = params["ADDVAR2"]
        NEWVAR2          = params["NEWVAR2"]
        ADDFLAMVAR       = params["ADDFLAMVAR"]
        NEWFLAMVAR       = params["NEWFLAMVAR"]
        ADDFLAMVAR2      = params["ADDFLAMVAR2"]
        NEWFLAMVAR2      = params["NEWFLAMVAR2"]
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
        ##############################################
        #    Parameters       #  
        ##############################################
        
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
        azimuthVF=plugin_imports.azimuthVF
        convert_xy=plugin_imports.convert_xy
        crossprod=plugin_imports.crossprod
        decision=plugin_imports.decision
        dotprod=plugin_imports.dotprod
        extract_vertices=plugin_imports.extract_vertices
        extract_urb_vertices_and_buffered=plugin_imports.extract_urb_vertices_and_buffered
        ftype=plugin_imports.ftype
        idxneigh=plugin_imports.idxneigh  
        get_neighbors=plugin_imports.get_neighbors
        adjust_coordinates=plugin_imports.adjust_coordinates
        nearest_indices=plugin_imports.nearest_indices
        promote_to_multipolygon=plugin_imports.promote_to_multipolygon
        process_flammables=plugin_imports.process_flammables 
        clean_and_reindex=plugin_imports.clean_and_reindex 
        insert_zero_at_the_beginning_of_1D_array=plugin_imports.insert_zero_at_the_beginning_of_1D_array
        insert_bigN_at_the_beginning_of_1D_array=plugin_imports.insert_bigN_at_the_beginning_of_1D_array
        
        ##############################################
        #    Set directory     #
        ##############################################
                    
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
        
        ##############################################
        #    Parameters     #
        ##############################################

        CREATE_INTERFACE = True   # Create even if file exists
        TESTIDX = True            # Test specific indices
        read = True               # Run the reading processing part of the script
        Main_Algo = True          # Run the main algorithm part of the script
        Select = True             # Run the select part of the script
        Save = True           # Save outputs

        ##############################################
        #    Test specific location     #
        ##############################################
        if TESTIDX:
            K = K
            KS = list(range(1, K+1))
            KF = KF
            KFS = list(range(1, KF+1))
            extraname = f"test-{extraname}" 
        
        
        ##############################################
        #    Test Point x0y0     #
        ##############################################
        x0y0=convert_xy(X, Y, urban_path)
        
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
                flam1 = gpd.read_file(flammable_path) 
                flam = promote_to_multipolygon(flam1)  
                if TESTIDX:
                    flam =process_flammables(flam, BOX) #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "clip"
                flam["idflam"] = range(1, len(flam) + 1)
                # save flam as geopackage?
                xy_flam = extract_vertices(flam) 
                if 'L3' not in xy_flam.columns or xy_flam['L3'].max() != len(flam):
                    raise ValueError("L3 is not properly indexed")
                idx_L1 = xy_flam['L1']
                idx_L2 = xy_flam['L2']
                M = 10 ** (1 + np.ceil(np.log10(idx_L2.max())).astype(int))
                Q = 10 ** (1 + np.ceil(np.log10(idx_L1.max())).astype(int))
                idx_feat_flam = xy_flam['L3']
                idx_part_flam = M * Q * idx_feat_flam + M * idx_L1 + idx_L2
                # june 2025: o create an artifial point (idx=0)  x=bigN, y=bigN. In neighbor search, when there is no eneighbor within search distance, the neighbor will be idx=0
                mat_flam = pd.DataFrame({
                    'x': insert_bigN_at_the_beginning_of_1D_array(np.round(xy_flam['x'])),
                    'y': insert_bigN_at_the_beginning_of_1D_array(np.round(xy_flam['y'])),
                    'idx_feat_flam': insert_zero_at_the_beginning_of_1D_array(idx_feat_flam),
                    'idx_part_flam':  insert_zero_at_the_beginning_of_1D_array(idx_part_flam.round())
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
                urb1 = gpd.read_file(urban_path) # now, this contains the original polygons plus the buffers, which can be selected with 'layer'="Buffered"
                urb = urb1.to_crs(flam.crs)
                if TESTIDX:
                    urb = process_flammables(urb,BOX)  #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "clip"
                urb['idurb'] = range(1, len(urb) + 1)   
                # save urb as geopackage?
                #xy_urb = extract_vertices(urb)
                xy_urb=extract_urb_vertices_and_buffered(urb,col='layer',value='Buffered') # returns also column "buffered" to distinguish original and "Buffered" vertices
                if 'L3' not in xy_urb.columns or xy_urb['L3'].max() != len(urb):
                    raise ValueError("L3 is not properly indexed")
                idx_L1 = xy_urb['L1']
                idx_L2 = xy_urb['L2']
                M = 10 ** (1 + np.ceil(np.log10(idx_L2.max())).astype(int))
                Q = 10 ** (1 + np.ceil(np.log10(idx_L1.max())).astype(int))
                idx_feat_urb = xy_urb['L3']
                idx_part_urb = M * Q * idx_feat_urb + M * idx_L1 + idx_L2
                # june 2025: o create an artifial point (idx=0)  x=bigN, y=bigN. In neighbor search, when there is no eneighbor within search distance, the neighbor will be idx=0
                mat_urb = pd.DataFrame({
                    'x': insert_bigN_at_the_beginning_of_1D_array(np.round(xy_urb['x'])),
                    'y': insert_bigN_at_the_beginning_of_1D_array(np.round(xy_urb['y'])),
                    'idx_feat_urb': insert_zero_at_the_beginning_of_1D_array(idx_feat_urb),
                    'idx_part_urb': insert_zero_at_the_beginning_of_1D_array(idx_part_urb.round()),
                    'buffered': insert_zero_at_the_beginning_of_1D_array(xy_urb['buffered'])
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
                # idx_vert_urb takes values 1,2,3,.... AFTER removal of duplicates
                mat_urb=clean_and_reindex(mat_urb,"idx_part_urb","idx_vert_urb") # Remove duplicates

                # build datatables -- however they are going to be converted back to dataframe in 209-210 !!!
                mat_urb_dt = dt.Frame(mat_urb)
                mat_flam_dt = dt.Frame(mat_flam)
                
                # search nearest flammable neighbor 
                idxUF_idx=nearest_indices(mat_urb_dt,mat_flam_dt,k=1,KDTREE_DIST_UPPERBOUND= KDTREE_DIST_UPPERBOUND,bigN=bigN)
                mat_flam_dt['idx_vert_urb'] = idxUF_idx # urban vertices of flam vertices
                idxFU_idx=nearest_indices(mat_flam_dt,mat_urb_dt,k=1, KDTREE_DIST_UPPERBOUND = KDTREE_DIST_UPPERBOUND,bigN=bigN)
                mat_urb_dt['idx_vert_flam'] = idxFU_idx # Flammable neighbors of urban vertices

            distances_squared = (mat_urb_dt["x"].to_numpy() - x0)**2 + (mat_urb_dt["y"].to_numpy() - y0)**2
            id0 = np.argmin(distances_squared) 
            # determining the K Flam neighbors up to distance D meters from each urban neighbor
            # Calculating the distance from each vertice of the urban polygons to each vertice within D meters  of the flammable polygons
            knn_idx,knn_dists=nearest_indices(mat_flam_dt,mat_urb_dt,k=K, return_distance=True,KDTREE_DIST_UPPERBOUND= KDTREE_DIST_UPPERBOUND,bigN=bigN) # neighbors urban X Flam
            FICHNAME_STEM= f"interface_K{K}_KF{KF}_limiar{round(limiar * 100)}_theta{limiartheta}_QT{Q}_{extraname}_{round(x0)}_y_{round(y0)}_d_{d}"
            FICHNAME= FICHNAME_STEM+ ".pickle"
            fichs = glob.glob(os.path.join(OUTPUT_FOLDER, FICHNAME))

            # save urb and flam

            urb=urb[['geometry','idurb']]
            urb.to_file(os.path.join(OUTPUT_FOLDER,f"urb_x_{round(x0)}_y_{round(y0)}_d_{d}.gpkg"), driver="GPKG")
            flam=flam[['geometry','idflam']]
            flam.to_file(os.path.join(OUTPUT_FOLDER,f"flam_x_{round(x0)}_y_{round(y0)}_d_{d}.gpkg"), driver="GPKG")
        

        ##############################################
        #    Main Algorithm   #
        ############################################## 
        if Main_Algo : 
            mat_urb_df = mat_urb_dt.to_pandas()
            mat_flam_df = mat_flam_dt.to_pandas()
            if CREATE_INTERFACE or TESTIDX or len(fichs) == 0:
                not_interface = np.full(len(mat_urb_df), True)  
                dF = np.full(len(mat_urb_df), POSVALUE)
                # Distance to farthest non-protected F
                dFplus = np.full(len(mat_urb_df), NEGVALUE)
                # Azimuth of the closest non-protected Flam (in degrees)
                azF = np.full(len(mat_urb_df), NEGVALUE)
                azFplus = np.full(len(mat_urb_df), NEGVALUE)
                # Index of the closest non-protected Flam
                iF = np.full(len(mat_urb_df), NEGVALUE)
                # Determine KF urban neighbors W of urban V
                # Get nearest neighbor 
                kvw_idx,kvw_dists = nearest_indices(mat_urb_dt,k=KF, return_distance=True,KDTREE_DIST_UPPERBOUND=KDTREE_DIST_UPPERBOUND,bigN=bigN) # (GROUP 1 of potential protectors) KF Urban neighbors of urban vertices  kvw$nn.idx[kvw$nn.idx==0]<-NA # NEW
                xV = mat_urb_df['x'].to_numpy()
                yV = mat_urb_df['y'].to_numpy()
                k=1
                for k in KS: # cycle through K FLAM neighbors of urban vertice 
                    print('k', k, 'out of', len(KS),'flammable neighbors')
                    threetimesprotected = np.full(len(mat_urb_df), True)
                    # the goal is to try to show that it is protected from its k-th flammable neighbor
                    # xyd gets the index of the k-th F-neighbor, and the distance to it
                    # Get the k-th F-neighbor index for urban vertices, allowing for NA/None values
                    idxF = knn_idx.iloc[:, k-1]
                    xF, yF, xFF, yFF, xFFF, yFFF, idxfeatF = get_neighbors(mat_df=mat_flam_df, idx=idxF, idxneigh_func=idxneigh,  in_type="flam",x_col='x', y_col='y', feat_col='idx_feat_flam')
                    # Flamm point closest to xF,yF over the edge (F,FF) - next
                    xFF,yFF = adjust_coordinates(xF, yF, xFF, yFF, xV, yV) # array
                    # Flamm point closest to xF,yF over the edge (F,FFF) -- prev
                    xFFF, yFFF=adjust_coordinates (xF, yF, xFFF,yFFF,xV,yV)
                    xFback=xF
                    yFback=yF
                    idxFviz=3 
                    for idxFviz in range(1, 4):
                        protected = np.full(len(mat_urb_df), False, dtype=bool) # Initialize protection status: it is not protected
                        if idxFviz == 2:
                            xF = xFF
                            yF = yFF
                        elif idxFviz == 3:
                            xF = xFFF
                            yF = yFFF
                        if not TESTIDX:
                            print(f"iteration {k} among F-neighbors and idxFviz={idxFviz} in 3")
                        # if idxfeatF isn't defined 
                        # # if idxfeatF is not defined:
                        xF = np.where(np.isnan(xF), bigN, xF)
                        yF = np.where(np.isnan(yF), bigN, yF)
                        idxfeatF = np.where(np.isnan(idxfeatF), NEGVALUE, idxfeatF)
                        # GROUP 1 of potential protectors:  KF Urban neighbors of urban vertices
                        # Dec 2018: moved outside  cycle GROUP 2: it should be k and not j, since kvw does not depend on the index of the flammable vertices
                        j =1
                        for j in KFS:  # Cycle through URB neighbors of selected Flam vertices GROUP 1
                            if j%20==0 and idxFviz==1 : print(j, 'out of', len(KFS), 'urban neighbors of V')
                            if not TESTIDX and j % 10 == 0:
                                print(f"GROUP1: iteration {j} among urban neighbors of V")
                            d2VW = kvw_dists.iloc[:, j-1] ** 2  # Distance between urban vertex V and its urban neighbor W
                            xW1, yW1, xWW1, yWW1, xWWW1, yWWW1, _ = get_neighbors( mat_df=mat_urb_df,  idx=kvw_idx.iloc[:, j-1],  idxneigh_func=idxneigh,  in_type="urb", x_col='x',  y_col='y', feat_col='idx_feat_urb' )
                            d2WF = (xW1 - xF) ** 2 + (yW1 - yF) ** 2  # distance from W to the k-th flammable neighbor F of V
                            # update protected
                            isprotected1 = decision(Q/100,KDTREE_DIST_UPPERBOUND,limiar,limiartheta,xV,yV,xF,yF,xW1,yW1,xWW1,yWW1,xWWW1,yWWW1,smallN,bigN,verbose=False,log_file="decision_table1.csv")
                            protected = protected | isprotected1
                        # GROUP 2 of potential protectors: KF Urban neighbors of selected flammable vertices
                        # urban neighbors of selected flammable vertices (xF,yF)
                        # nn2 does not accept NAs
                        query = dt.Frame(np.column_stack((xF, yF)), names=['x', 'y'])
                        kfw_idx, kfw_dists = nearest_indices(mat_urb_dt,query,k=KF, return_distance=True,KDTREE_DIST_UPPERBOUND=KDTREE_DIST_UPPERBOUND,bigN=bigN)
                        for j in KFS:  # Cycle through URB neighbors of selected Flam vertices GROUP 1
                            if j%20==0 and idxFviz==1 : print(j, 'out of', len(KFS), 'urban neighbors of Flam neighbors of V')
                            if not TESTIDX and j % 10 == 0:
                                print(f"GROUP2: iteration {j} among urban neighbors of Flam neighbors of V")
                            d2WF = kfw_dists.iloc[:, j-1] ** 2  # Distance between urban vertex V and its urban neighbor W
                            xW2, yW2, xWW2, yWW2, xWWW2, yWWW2, _ = get_neighbors( mat_df=mat_urb_df,  idx=kfw_idx.iloc[:, j-1], idxneigh_func=idxneigh,  in_type="urb", x_col='x',  y_col='y', feat_col='idx_feat_urb' )
                            d2VW = (xW2 - xV) ** 2 + (yW2 - yV) ** 2  # distance from W to the k-th flammable neighbor F of V
                            isprotected2 = decision(Q/100,KDTREE_DIST_UPPERBOUND,limiar,limiartheta,xV,yV,xF,yF,xW2,yW2,xWW2,yWW2,xWWW2,yWWW2,smallN,bigN,verbose=False,log_file="decision_table2.csv")
                            protected = protected | isprotected2
                        # set2019: define new variables d2VF, azVF and idxVF that are updated to depend on the closest neighbor among F,FF,FFF
                        # Calculate the current squared distance between V and F
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
                    # notinterface will be FALSE if V is not protected from its k-th F-neighbor
                    # 28ago2019: do like dF to set indF from current idxfeatF, and azF from current azVF
                    iF = (threetimesprotected * iF) + \
                    (~threetimesprotected * ((d2VF < dF**2) * idxVF + (d2VF >= dF**2) * iF))
                    azF = (threetimesprotected * azF) + \
                    (~threetimesprotected * ((d2VF < dF**2) * azVF + \
                                                        (d2VF >= dF**2) * azF))
                    dF = (threetimesprotected * dF) + \
                    (~threetimesprotected * ((d2VF < dF**2) * np.sqrt(d2VF) + \
                                                        (d2VF >= dF**2) * dF))
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
            xyd = dt.Frame({
            'x': mat_urb_df['x'].to_list(),  
            'y': mat_urb_df['y'].to_list(), 
            'buffered':  mat_urb_df['buffered'].to_list(),  
            'idx_part_u': mat_urb_df['idx_part_urb'].to_list(),  
            'idx_feat_u': mat_urb_df['idx_feat_urb'].to_list(), 
            'idx_vert_u': mat_urb_df['idx_vert_urb'].to_list(),  
            'vert_type': ftype(dF, KDTREE_DIST_UPPERBOUND).tolist(),  
            'idx_feat_f': mat_flam_df.loc[idxF, 'idx_feat_flam'].values,  
            'dist_feat_f': knn_dists.iloc[:, 0].to_list(),  # Distance to closest flammable feature
            'd': dF.tolist(),  # Distance variable (NEW)
            'az': azF.tolist(),  # Azimuth variable
            'iF': iF.tolist(),  # Index of closest non-protected flammable feature
            'interface': interface.astype(int).tolist()  # Interface variable as integer
        })

        # Remove first row:  artifact point x=bigN, y=bigN
        xyd = xyd[1:, :]

        # remove buffered vertices (jun 2025)
        xyd = xyd[dt.f.buffered != 1, :]

        # sort by idx_vert_u (necessary?)
        xyd=xyd[:, :, dt.sort(dt.f.idx_vert_u)].copy()

        xyd[dt.f.d == POSVALUE, 'd'] = NEGVALUE # Replace POSVALUE with NEGVALUE for distances dF in the 'd' column
        xyd[dt.isna(dt.f.iF), 'iF'] = NEGVALUE # Replace NaN values in iF with NEGVALUE
        # add distances of segments
        xydL = xyd[2:, :]
        xydR = xyd[:-2, :]
        xydL.names = [f"{name}_L" for name in xyd.names]
        xydR.names = [f"{name}_R" for name in xyd.names]
        xyd_middle = xyd[1:-1, :]
        xydDT = dt.cbind(xyd_middle, xydL, xydR)
        xydDT = xydDT[:, :, dt.sort(dt.f.idx_vert_u)]
        # determine length of edges
        xydDT[:, dt.update(lengthL=np.sqrt((xydDT['x_L'].to_numpy() - xydDT['x'].to_numpy())**2 + 
                                        (xydDT['y_L'].to_numpy() - xydDT['y'].to_numpy())**2))]
        xydDT[:, dt.update(lengthR=np.sqrt((xydDT['x_R'].to_numpy() - xydDT['x'].to_numpy())**2 + 
                                        (xydDT['y_R'].to_numpy() - xydDT['y'].to_numpy())**2))]
        xydDT[dt.f.idx_part_u != dt.f.idx_part_u_L, dt.update(lengthL=NEGVALUE)]
        xydDT[dt.f.idx_part_u != dt.f.idx_part_u_R, dt.update(lengthR=NEGVALUE)]
        # azimuth of segments 
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
        # determine when segments start/end
        xydDT[:, dt.update(linkR=(dt.f.interface | dt.f.interface_R) & 
                        (dt.f.idx_part_u == dt.f.idx_part_u_R) & 
                        (dt.math.abs(dt.f.idx_vert_u - dt.f.idx_vert_u_R) <= 1))] # same part and successive vertex
        xydDT[:, dt.update(linkL=(dt.f.interface | dt.f.interface_L) & 
                        (dt.f.idx_part_u == dt.f.idx_part_u_L) & 
                        (dt.math.abs(dt.f.idx_vert_u - dt.f.idx_vert_u_L) <= 1))] # same part and successive vertex
        # sequences 0/1 and segment numbering
        xydDT[:, dt.update(steplinkL=dt.shift(dt.f.linkL, -1) - dt.f.linkL)]
        xydDT[:, dt.update(segmentL=dt.cumsum((dt.f.steplinkL >= 0) * dt.f.steplinkL))]
        xydDT[:, dt.update(steplinkR=dt.f.linkR - dt.shift(dt.f.linkR))]
        xydDT[:, dt.update(segmentR=1 + dt.cumsum((dt.f.steplinkR <= 0) * dt.math.abs(dt.f.steplinkR)))]
        # remove segment numbers when not interface
        xydDT[(dt.f.interface == False) & (dt.f.interface_R == False), dt.update(segmentR=NEGVALUE)]
        xydDT[(dt.f.interface == False) & (dt.f.interface_L == False), dt.update(segmentL=NEGVALUE)]
        #xydDT[:, dt.update(azsegmentL=NEGVALUE)]
        
        colnames_xydDT = xydDT.names
        # variables to keep
        VARS = ['idx_feat_u', 'x', 'y', 'idx_part_u', 'idx_vert_u', 'vert_type', 'idx_feat_f', 'dist_feat_f', 'd', 'az', 'iF', 'interface',
                'linkL', 'linkR', 'lengthL', 'lengthR', 'segmentL', 'segmentR', 'azimuthL', 'azimuthR']

        xydDT = xydDT[:, VARS]

        # Save to CSV
        if Save: 
            VARS = ['x', 'y', 'vert_type', 'linkL', 'linkR', 'idx_vert_u',  'idx_part_u',  'interface', 'd']
            xydDT = xydDT[:, VARS]
            xydDT_df = xydDT.to_pandas()
            output_path33 = os.path.join(OUTPUT_FOLDER,FICHNAME_STEM+".csv")
            print(output_path33)
            xydDT_df.to_csv(output_path33, sep=',', index=False)

        start = time.time()
        # -------------------------------------------------------------
        # 1.5) Show status messages
        # -------------------------------------------------------------

        # Show initial "starting" message
        iface.messageBar().pushMessage("🟡 Starting", "Preparing to load layers...", level=0, duration=3)

        # Show persistent "loading..." message
        msg = iface.messageBar().createMessage("Loading layers...", "Please wait")
        iface.messageBar().pushWidget(msg, level=0)
        # -------------------------------------------------------------
        # 1) Prepare your data & CRS
        # -------------------------------------------------------------
        interface_pts_df = xydDT_df
        matFlamDF = mat_flam_dt.to_pandas()
        matUrbDF = mat_urb_dt.to_pandas()

        crs_code = flam.crs.to_epsg() if hasattr(flam, "crs") and flam.crs else 4326
        crs_str = f"EPSG:{crs_code}"

        # -------------------------------------------------------------
        # 2) Create all layers 
        # -------------------------------------------------------------
        interface_pts_layer = load_datatable_as_point_layer(interface_pts_df, "Interface_Points", crs_code, "x", "y")
        flam_pt_layer = load_datatable_as_point_layer(matFlamDF, "Flam_Vertices", crs_code, "x", "y")
        urb_pt_layer = load_datatable_as_point_layer(matUrbDF, "Urb_Vertices", crs_code, "x", "y")
        flam_poly = create_vector_layer_from_gdf(flam, "Flammable_Polygons", crs_str)
        urb_poly = create_vector_layer_from_gdf(urb, "Urban_Polygons", crs_str)
        flam_layer=create_vector_layer_from_gdf(flam1, "flammable_Area", crs_str)
        urb_layer=create_vector_layer_from_gdf(urb1, "Urban_Area", crs_str)
        # -------------------------------------------------------------
        # 2.1) Style layers
        # -------------------------------------------------------------
        # Flammable area – light red 
        flam_layer.renderer().symbol().setColor(QColor("#fcae91"))  # light red
        flam_layer.renderer().symbol().setOpacity(0.5)
        
        # Flammable polygons – light red and semi-transparent
        flam_poly.renderer().symbol().setColor(QColor("#fcae91"))  # light red
        flam_poly.renderer().symbol().setOpacity(0.9)

        # Flammable points – red
        flam_symbol = flam_pt_layer.renderer().symbol()
        flam_symbol.setColor(QColor("red"))
        flam_symbol.setSize(2.0)
        # Urban area – light blue and semi-transparent
        urb_layer.renderer().symbol().setColor(QColor("#a6bddb"))  # light blue
        urb_layer.renderer().symbol().setOpacity(0.2)
        
        # Urban polygons – light blue and semi-transparent
        urb_poly.renderer().symbol().setColor(QColor("#a6bddb"))  # light blue
        urb_poly.renderer().symbol().setOpacity(0.9)

        # Urban points – dark blue
        urb_symbol = urb_pt_layer.renderer().symbol()
        urb_symbol.setColor(QColor("darkblue"))
        urb_symbol.setSize(2.0)

        # -------------------------------------------------------------
        # 3) Helper to add & position each layer
        # -------------------------------------------------------------
        def add_layer(layer, name, position):
            if not layer or not layer.isValid():
                QMessageBox.warning(None, "Layer Load Error", f"Layer '{name}' failed to load.")
                return
            project = QgsProject.instance()
            root = project.layerTreeRoot()
            project.addMapLayer(layer, addToLegend=False)
            if position.lower() == "top":
                root.insertLayer(0, layer)
            else:
                root.addLayer(layer)
            QMessageBox.information(None, "Layer Loaded", f"Layer '{name}' added at the {position} of the legend.")

        # -------------------------------------------------------------
        # 4) Add OpenStreetMap as an XYZ‐tile basemap (fallback)
        # -------------------------------------------------------------
        osm_uri = (
            "type=xyz"
            "&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            "&zmin=0"
            "&zmax=19"
            "&crs=EPSG:3857"
        )
        osm_layer = QgsRasterLayer(osm_uri, "OpenStreetMap", "wms")

        # -------------------------------------------------------------
        # 5) Add all layers to the project
        # -------------------------------------------------------------
        add_layer(flam_layer, "Flammable_layer", "bottom")
        add_layer(urb_layer, "Urban_layer", "bottom")
        add_layer(flam_poly, "Flammable_Polygons", "bottom")
        add_layer(urb_poly, "Urban_Polygons", "bottom")
        add_layer(osm_layer, "OpenStreetMap", "bottom")
        add_layer(flam_pt_layer, "Flam_Vertices", "top")
        add_layer(urb_pt_layer, "Urb_Vertices", "top")
        add_layer(interface_pts_layer, "Interface_Points", "top")
        # -------------------------------------------------------------
        # 5.5) Style interface_pts_layer (interface == 1)
        # -------------------------------------------------------------
        symbol = QgsSymbol.defaultSymbol(interface_pts_layer.geometryType())
        root_rule = QgsRuleBasedRenderer.Rule(None)
        rule = QgsRuleBasedRenderer.Rule(symbol)
        rule.setFilterExpression('"interface" = 1')
        rule.setLabel("interface = 1")
        root_rule.appendChild(rule)
        interface_pts_layer.setRenderer(QgsRuleBasedRenderer(root_rule))

        field_name = "vert_type"
        idx = interface_pts_layer.fields().indexOf(field_name)
        values = sorted(interface_pts_layer.uniqueValues(idx))
        n = len(values)

        style = QgsStyle().defaultStyle()
        ramp = style.colorRamp("Random colors")
        fallback_colors = [QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]

        D = 500
        labels = {
            1: "Direct interface",
            2: "0 < d ≤ 100",
            3: "100 < d ≤ 250",
            4: f"250 < d ≤ {D}",
            5: "Indirect interface",
        }

        root_rule = QgsRuleBasedRenderer.Rule(None)
        for i, val in enumerate(values):
            sym = QgsSymbol.defaultSymbol(interface_pts_layer.geometryType())
            if ramp:
                t = float(i) / (n - 1) if n > 1 else 0.0
                sym.setColor(ramp.color(t))
            else:
                sym.setColor(fallback_colors[i])
            rule = QgsRuleBasedRenderer.Rule(sym)
            rule.setFilterExpression(f'"interface" = 1 AND "{field_name}" = {val}')
            rule.setLabel(labels.get(val, str(val)))
            root_rule.appendChild(rule)

        interface_pts_layer.setRenderer(QgsRuleBasedRenderer(root_rule))
        interface_pts_layer.triggerRepaint()
        # -------------------------------------------------------------
        # 6) Generate and display line segments from Interface_Points
        # -------------------------------------------------------------
        MAXTYPE = 5  # Define max type for line drawing

        features = [f for f in interface_pts_layer.getFeatures()]
        features.sort(key=lambda f: (int(f['idx_part_u']), int(f['idx_vert_u'])))

        sequences = []
        types = []
        current_sequence = []
        P_, type_, x_, y_, d_ = None, None, None, None, None

        for f in features:
            try:
                x = f.geometry().asPoint().x()
                y = f.geometry().asPoint().y()
                P = int(f['idx_part_u'])
                type_val = f['vert_type']
                d = f['d']
                idx = int(f['idx_vert_u'])
                type_str = str(int(float(type_val)))  # Normalize type
            except Exception as e:
                print(f"Skipping feature due to error: {e}")
                continue

            if type_ is None: type_ = type_str
            if P_ is None: P_ = P
            if d_ is None: d_ = d
            if x_ is None: x_ = x
            if y_ is None: y_ = y

            if type_str == type_ and P == P_:
                current_sequence.append((x, y))
                P_, d_, x_, y_ = P, d, x, y

            elif type_str != type_ and P == P_:
                # Insert midpoint to avoid sharp type transitions
                mid_x, mid_y = (x + x_) * 0.5, (y + y_) * 0.5
                current_sequence.append((mid_x, mid_y))
                if len(current_sequence) >= 2 and int(type_) < MAXTYPE:
                    sequences.append(current_sequence)
                    types.append(type_)
                current_sequence = [(mid_x, mid_y), (x, y)]
                P_, d_, x_, y_, type_ = P, d, x, y, type_str

            else:
                if len(current_sequence) >= 2 and int(type_) < MAXTYPE:
                    sequences.append(current_sequence)
                    types.append(type_)
                current_sequence = [(x, y)]
                P_, d_, x_, y_, type_ = P, d, x, y, type_str

        # Add the last sequence
        if len(current_sequence) >= 2 and int(type_) < MAXTYPE:
            sequences.append(current_sequence)
            types.append(type_)


        # -------------------------------------------------------------
        # 7) Create and style line layer
        # -------------------------------------------------------------
        line_layer = QgsVectorLayer("LineString?crs=" + interface_pts_layer.crs().authid(), "Interface_Lines", "memory")
        prov = line_layer.dataProvider()
        prov.addAttributes([QgsField("type", QVariant.String)])
        line_layer.updateFields()

        # Add to map BEFORE editing
        QgsProject.instance().addMapLayer(line_layer, True)

        line_layer.startEditing()
        for i, seq in enumerate(sequences):
            if len(seq) >= 2:
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in seq]))
                feat.setAttributes([types[i]])
                prov.addFeature(feat)
        line_layer.commitChanges()

        # Save layer reference
        self.interface_lines_layer = line_layer

        # -------------------------------------------------------------
        # 8) Style lines by type
        # -------------------------------------------------------------
        categories = []
        for i in range(1, MAXTYPE):
            if i == 1:
                color = QColor(255, 0, 0)  # Red
            elif i == 3:
                color = QColor(255, 165, 0)  # Orange
            elif i == 4:
                color = QColor(255, 255, 0)  # Yellow
            else:
                # Gradient for missing defined cases
                r, g, b = 255, 0, 0
                g = int(165 * (i - 1) / (MAXTYPE - 2))
                color = QColor(r, g, b)

            symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
            symbol.setColor(color)
            symbol.setWidth(2)
            category = QgsRendererCategory(str(i), symbol, f"type {i}")
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer("type", categories)
        line_layer.setRenderer(renderer)
        line_layer.triggerRepaint()

        # -------------------------------------------------------------
        # 9) Final refresh to display everything
        # -------------------------------------------------------------
        self.iface.mapCanvas().setExtent(line_layer.extent())
        self.iface.mapCanvas().refresh()
        iface.messageBar().clearWidgets()
        iface.messageBar().pushMessage("Layers loaded", f"Took {time.time() - start:.2f} seconds", level=0, duration=5)