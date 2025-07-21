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
from constants import * 
from parameters import *
from Functions.bounding_box import *
from Functions.preprocessing import *
from Functions.extract_level import * 
from Functions.index import * 
from Functions.main_script_functions import * 
from Functions.nearest_neighbor_function import *
from Functions.decision import * 
from Functions.dot_product import * 
from Functions.cross_product import * 
from Functions.ftype import * 
from Functions.azimuthVF_function import * 
from Functions.Drawing_plot import * 
from Functions.convert_3763_XY_into_urban_closest_vertex import *

##############################################
    #    Set directory     #
##############################################
USER='M'
if USER=='A'
    INPUT_FOLDER = "C:\\Users\\aziza\\Desktop\\Interface_Github\\Data"  # Data Folder
    OUTPUT_FOLDER =  "C:\\Users\\aziza\\Desktop\\Interface_Github\\Output"  
else:
    INPUT_FOLDER = r"C:\temp\aziza\Direct_Indirect_Interface\Interface_Github\Data" 
    OUTPUT_FOLDER = r"C:\temp\aziza\Direct_Indirect_Interface\Interface_Github\Output" 

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
# x0y0 = pd.DataFrame([{'X': -97749.6, 'Y': -102314.8}])
# x0y0 = pd.DataFrame([{'X': -97731.1, 'Y': -101627.2}])
# x0y0 = pd.DataFrame([{'X': -97322.97, 'Y': -101139.99}])
# x0y0 = pd.DataFrame([{'X': -97403.9, 'Y': -101304.0}])
input_coords= {'X': -97593.9, 'Y': -101665.2} # -102226.806,-91783.807
# X,Y=[-101429.975,-92435.477]
X,Y=[-101416.832,-92411.277]

x0y0=convert_3763_XY_into_urban_closest_vertex(X,Y, urban_path)

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
        mat_urb=clean_and_reindex(mat_urb,"idx_part_urb","idx_vert_urb") # Remove duplicates

        mat_urb_dt = dt.Frame(mat_urb)
        mat_flam_dt = dt.Frame(mat_flam)
        
        # search nearest flammable neighbor 
        idxUF_idx=nearest_indices(mat_urb_dt,mat_flam_dt,k=1)
        mat_flam_dt['idx_vert_urb'] = idxUF_idx # urban vertices of flam vertices
        idxFU_idx=nearest_indices(mat_flam_dt,mat_urb_dt,k=1)
        mat_urb_dt['idx_vert_flam'] = idxFU_idx # Flammable neighbors of urban vertices
    distances_squared = (mat_urb_dt["x"].to_numpy() - x0)**2 + (mat_urb_dt["y"].to_numpy() - y0)**2
    id0 = np.argmin(distances_squared) 
    # determining the K Flam neighbors up to distance D meters from each urban neighbor
    # Calculating the distance from each vertice of the urban polygons to each vertice within D meters  of the flammable polygons
    knn_idx,knn_dists=nearest_indices(mat_flam_dt,mat_urb_dt,k=K, return_distance=True) # neighbors urban X Flam
    FICHNAME= f"interface_K{K}_KF{KF}_limiar{round(limiar * 100)}_maxdist{MAXDIST}-maxtheta{limiartheta}-{extraname}.pickle"
    fichs = glob.glob(os.path.join(OUTPUT_FOLDER, f"{FICHNAME}.pickle"))
    
    
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
        kvw_idx,kvw_dists = nearest_indices(mat_urb_dt,k=KF, return_distance=True) # (GROUP 1 of potential protectors) KF Urban neighbors of urban vertices  kvw$nn.idx[kvw$nn.idx==0]<-NA # NEW
        xV = mat_urb_df['x']
        yV = mat_urb_df['y']
        ###### first plot
        if DRAWSEGMENTS or DRAWPOINTS:
            fig, ax = plt.subplots(figsize=(10, 10))
            full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, mode='plot_cropped_background_layout') #background
            full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, x0=x0, y0=y0, d=d, mode='add_filtered_points') # urban vertices inside of the circle
        k=1
        for k in KS: # cycle through K FLAM neighbors of urban vertice 
            threetimesprotected = np.full(len(mat_urb_df), True)
            # the goal is to try to show that it is protected from its k-th flammable neighbor
            # xyd gets the index of the k-th F-neighbor, and the distance to it
            # Get the k-th F-neighbor index for urban vertices, allowing for NA/None values
            idxF = knn_idx.iloc[:, k-1]
            xF, yF, xFF, yFF, xFFF, yFFF, idxfeatF = get_neighbors(mat_df=mat_flam_df, idx=idxF, idxneigh_func=idxneigh,  in_type="flam",x_col='x', y_col='y', feat_col='idx_feat_flam')
            ####### 2nd plot
            if DRAWSEGMENTS or DRAWPOINTS:
                full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX,x0=x0, y0=y0, d=d, xFF=xFF, xF=xF, xFFF=xFFF, yFF=yFF, yF=yF, yFFF=yFFF, mode='plot_segments')
            # Flamm point closest to xF,yF over the edge (F,FF) - next
            xFF,yFF = adjust_coordinates(xF, yF, xFF, yFF, xV, yV)
            # Flamm point closest to xF,yF over the edge (F,FFF) -- prev
            xFFF, yFFF=adjust_coordinates (xF, yF, xFFF,yFFF,xV,yV)
            xFback=xF
            yFback=yF
            if DRAWSEGMENTS or DRAWPOINTS:
                full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, xFback=xFback, yFback=yFback, xFF=xFF, xFFF=xFFF, id0=id0, mode='plot_labels')
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
                xF = np.where(np.isnan(xF), bigN, xF)
                yF = np.where(np.isnan(yF), bigN, yF)
                idxfeatF = np.where(np.isnan(idxfeatF), NEGVALUE, idxfeatF)
                if DRAWSEGMENTS: 
                    full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, x0=x0, y0=y0, d=d,  xFF=xFF, xF=xF, xFFF=xFFF, yFF=yFF, yF=yF, yFFF=yFFF, valid_idxF=idxF,xFback=xFback, yFback=yFback, id0=id0, xV=xV, yV=yV,  idxFviz=idxFviz, mode='plot_points')
                # GROUP 1 of potential protectors:  KF Urban neighbors of urban vertices
                # Dec 2018: moved outside  cycle GROUP 2: it should be k and not j, since kvw does not depend on the index of the flammable vertices
                j =1
                for j in KFS:  # Cycle through URB neighbors of selected Flam vertices GROUP 1
                    if not TESTIDX and j % 10 == 0:
                        print(f"GROUP1: iteration {j} among urban neighbors of V")
                    d2VW = kvw_dists.iloc[:, j-1] ** 2  # Distance between urban vertex V and its urban neighbor W
                    xW1, yW1, xWW1, yWW1, xWWW1, yWWW1, _ = get_neighbors( mat_df=mat_urb_df,  idx=kvw_idx.iloc[:, j-1],  idxneigh_func=idxneigh,  in_type="urb", x_col='x',  y_col='y', feat_col='idx_feat_urb' )
                    d2WF = (xW1 - xF) ** 2 + (yW1 - yF) ** 2  # distance from W to the k-th flammable neighbor F of V
                    # update protected
                    isprotected1 = decision(D,limiar,limiartheta,xV,yV,xF,yF,xW1,yW1,xWW1,yWW1,xWWW1,yWWW1,verbose=False,log_file="decision_table1.csv")
                    if DRAWSEGMENTS or DRAWPOINTS:
                        full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, xW=xW1, yW=yW1, xWW=xWW1, yWW=yWW1, xWWW=xWWW1, yWWW=yWWW1, xF=xF, yF=yF, xV=xV, yV=yV, id0=id0, mode='draw_points_g1')
                    protected1 = protected | isprotected1
                # GROUP 2 of potential protectors: KF Urban neighbors of selected flammable vertices
                # urban neighbors of selected flammable vertices (xF,yF)
                # nn2 does not accept NAs
                query = dt.Frame(np.column_stack((xF, yF)), names=['x', 'y'])
                kfw_idx, kfw_dists = nearest_indices(mat_urb_dt,query,k=KF, return_distance=True)
                for j in KFS:  # Cycle through URB neighbors of selected Flam vertices GROUP 1
                    if not TESTIDX and j % 10 == 0:
                        print(f"GROUP2: iteration {j} among urban neighbors of Flam neighbors of V")
                    d2WF = kfw_dists.iloc[:, j-1] ** 2  # Distance between urban vertex V and its urban neighbor W
                    xW2, yW2, xWW2, yWW2, xWWW2, yWWW2, _ = get_neighbors( mat_df=mat_urb_df,  idx=kfw_idx.iloc[:, j-1], idxneigh_func=idxneigh,  in_type="urb", x_col='x',  y_col='y', feat_col='idx_feat_urb' )
                    d2VW = (xW2 - xV) ** 2 + (yW2 - yV) ** 2  # distance from W to the k-th flammable neighbor F of V
                    isprotected2 = decision(D,limiar,limiartheta,xV,yV,xF,yF,xW2,yW2,xWW2,yWW2,xWWW2,yWWW2,verbose=False,log_file="decision_table2.csv")
                    if DRAWSEGMENTS or DRAWPOINTS:
                        full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, xW=xW2, yW=yW2, xWW=xWW2, yWW=yWW2, xWWW=xWWW2, yWWW=yWWW2, xF=xF, yF=yF, xV=xV, yV=yV, id0=id0, mode='draw_points_g2')
                    protected2 = protected | isprotected2
                protected = protected1 | protected2
                if DRAWSEGMENTS or DRAWPOINTS:
                    full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, protected=protected, xV=xV, yV=yV, xF=xF, yF=yF, id0=id0, idxFviz=idxFviz, mode='draw_last_segments')

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
# # # Show the final plot # # #
if DRAWSEGMENTS or DRAWPOINTS:
    plt.tight_layout()
    plt.show()


##############################################
    #   select interface and add features   #
############################################## 

if Select: 
    xyd = dt.Frame({
        'x': mat_urb_df['x'].to_list(),  
        'y': mat_urb_df['y'].to_list(),  
        'idx_part_u': mat_urb_df['idx_part_urb'].to_list(),  
        'idx_feat_u': mat_urb_df['idx_feat_urb'].to_list(), 
        'idx_vert_u': mat_urb_df['idx_vert_urb'].to_list(),  
        'vert_type': ftype(dF, D).tolist(),  
        'idx_feat_f': mat_flam_df.loc[idxF, 'idx_feat_flam'].values,  
        'dist_feat_f': knn_dists.iloc[:, 0].to_list(),  # Distance to closest flammable feature
        'd': dF.tolist(),  # Distance variable (NEW)
        'az': azF.tolist(),  # Azimuth variable
        'iF': iF.tolist(),  # Index of closest non-protected flammable feature
        'interface': interface.astype(int).tolist()  # Interface variable as integer
    })


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
                    (dt.math.abs(dt.f.idx_vert_u - dt.f.idx_vert_u_R) <= 1))]
    xydDT[:, dt.update(linkL=(dt.f.interface | dt.f.interface_L) & 
                    (dt.f.idx_part_u == dt.f.idx_part_u_L) & 
                    (dt.math.abs(dt.f.idx_vert_u - dt.f.idx_vert_u_L) <= 1))]
    # sequences 0/1 and segment numbering
    xydDT[:, dt.update(steplinkL=dt.shift(dt.f.linkL, -1) - dt.f.linkL)]
    xydDT[:, dt.update(segmentL=dt.cumsum((dt.f.steplinkL >= 0) * dt.f.steplinkL))]
    xydDT[:, dt.update(steplinkR=dt.f.linkR - dt.shift(dt.f.linkR))]
    xydDT[:, dt.update(segmentR=1 + dt.cumsum((dt.f.steplinkR <= 0) * dt.math.abs(dt.f.steplinkR)))]
    # remove segment numbers when not interface
    xydDT[(dt.f.interface == False) & (dt.f.interface_R == False), dt.update(segmentR=NEGVALUE)]
    xydDT[(dt.f.interface == False) & (dt.f.interface_L == False), dt.update(segmentL=NEGVALUE)]
    xydDT[:, dt.update(azsegmentL=NEGVALUE)]
    colnames_xydDT = xydDT.names
    # variables to keep
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

    # create point sf for outut with all relevant information on each urban vertex
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

    # if not TESTIDX:
    #     output_path = os.path.join(FOLDER, f"points-{OUTNAME}")
    #     interface_pts.to_csv(output_path, index=False, sep='\t')  

    # Save to CSV
    if Save: 
        xydDT_df = xydDT.to_pandas()
        output_path33 = os.path.join(OUTPUT_FOLDER,"xydDT.csv")
        xydDT_df.to_csv(output_path33, sep=',', index=False)
