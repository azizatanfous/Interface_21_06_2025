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
from Functions.extract_urb_level_and_buffered import *
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
from Functions.Get_directory import get_project_directories

##############################################
    #    Set directory     #
##############################################
INPUT_FOLDER, OUTPUT_FOLDER = get_project_directories()
option = "altorisco"  # Choose between "altorisco" (high-risk) or "todos" (all areas)
if option == "altorisco":
    inputFlamm = "high_risk_sintra.shp"  # High-risk combustible areas
elif option == "todos":
    inputFlamm = "all_risk_sintra.shp"  # All combustible areas 

urban_file = "urban_sintra.shp"  # Buffered Urban area file. Atributo 'layer'="Buffered" indica ods polígonos do buffer negativo

if option == "altorisco":
    extraname = "AR2019"#"8set19GLisboaAltoRisco"  
elif option == "todos":
    extraname = "All2019"#"8set19GLisboaTodos"  

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


##############################################
    #    Test Point x0y0     #  coordinate system : 'EPSG:3763'
##############################################
# X,Y=[-101429.975,-92435.477]
# X,Y=[-101416.832,-92411.277]
X,Y=[-97403.9,-101304.0]
# X,Y=[-97337.8,-101021.2]
# X,Y=[-101416.832,-92411.277]
# X,Y=[-101296.8,-92594.3]
# X,Y=[-101352.3,-92686.7]
# X,Y=[-107141.963,-92168.828]
# X,Y=[-107141.963,-92168.828] # Figure_1
# X,Y=[-107110.014,-92262.408] # Figure 2
# X,Y=[-101416.832,-92411.277] # exemplo Aziza
# X,Y=[-101380,-92395] # exemplo Aziza, ao lado
# X,Y=[-100556.002,-93329.993] # exemplo segmento com um vertice 
# X,Y=[-97885.426,-88204.763] # outro local em Sintra

x0y0=convert_3763_XY_into_urban_closest_vertex(X,Y, urban_path)

##############################################
    #    Bounding Box    # 
##############################################
x0 = x0y0["X"].values[0]  
y0 = x0y0["Y"].values[0]  
BOX = create_bounding_box(x0,y0, d_box) # Creates a bounding box centered at (x0, y0) with distance 'd'


##############################################
    #    Reading Part #
##############################################
if read:
    if CREATE_INTERFACE or TESTIDX:
        # Process Flammable Data
        flam = gpd.read_file(flammable_path) 
        flam = promote_to_multipolygon(flam)  
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
        urb = gpd.read_file(urban_path) # now, this contains the original polygons plus the buffers, which can be selected with 'layer'="Buffered"
        urb = urb.to_crs(flam.crs)
        if TESTIDX:
            urb = process_flammables(urb,BOX)  #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "clip"
        urb['idurb'] = range(1, len(urb) + 1)   
        # save urb as geopackage?
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
        # It is because datatable is better for search nearest_indices while dataframe takes a lot of time . 
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
    FICHNAME_STEM= f"interface_K{K}_KF{KF}_limiar{round(limiar * 100)}_theta{limiartheta}_QT{QT}_{extraname}_{round(x0)}_y_{round(y0)}_d_{d_box}"
    FICHNAME= FICHNAME_STEM+ ".pickle"
    fichs = glob.glob(os.path.join(OUTPUT_FOLDER, FICHNAME))

    # save urb and flam

    urb=urb[['geometry','idurb']]
    urb.to_file(os.path.join(OUTPUT_FOLDER,f"urb_x_{round(x0)}_y_{round(y0)}_d_{d_box}.gpkg"), driver="GPKG")
    flam=flam[['geometry','idflam']]
    flam.to_file(os.path.join(OUTPUT_FOLDER,f"flam_x_{round(x0)}_y_{round(y0)}_d_{d_box}.gpkg"), driver="GPKG")

    
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
        ###### first plot
        if DRAWSEGMENTS or DRAWPOINTS:
            fig, ax = plt.subplots(figsize=(10, 10))
            full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, mode='plot_cropped_background_layout') #background
            full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, x0=x0, y0=y0, d=d_box, mode='add_filtered_points') # urban vertices inside of the circle
            #plt.tight_layout()
            #plt.show()
        k=1
        for k in KS: # cycle through K FLAM neighbors of urban vertice 
            print('k', k, 'out of', len(KS),'flammable neighbors')
            threetimesprotected = np.full(len(mat_urb_df), True)
            # the goal is to try to show that it is protected from its k-th flammable neighbor
            # xyd gets the index of the k-th F-neighbor, and the distance to it
            # Get the k-th F-neighbor index for urban vertices, allowing for NA/None values
            idxF = knn_idx.iloc[:, k-1]
            #print(mat_flam_df)
            #print(max(idxF))
            xF, yF, xFF, yFF, xFFF, yFFF, idxfeatF = get_neighbors(mat_df=mat_flam_df, idx=idxF, idxneigh_func=idxneigh,  in_type="flam",x_col='x', y_col='y', feat_col='idx_feat_flam')
            ####### 2nd plot
            if DRAWSEGMENTS or DRAWPOINTS:
                full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX,x0=x0, y0=y0, d=d_box, xFF=xFF, xF=xF, xFFF=xFFF, yFF=yFF, yF=yF, yFFF=yFFF, mode='plot_segments')
            # Flamm point closest to xF,yF over the edge (F,FF) - next
            xFF,yFF = adjust_coordinates(xF, yF, xFF, yFF, xV, yV) # array
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
                    full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, x0=x0, y0=y0, d=d_box,  xFF=xFF, xF=xF, xFFF=xFFF, yFF=yFF, yF=yF, yFFF=yFFF, valid_idxF=idxF,xFback=xFback, yFback=yFback, id0=id0, xV=xV, yV=yV,  idxFviz=idxFviz, mode='plot_points')
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
                    isprotected1 = decision(QT/100,KDTREE_DIST_UPPERBOUND,limiar,limiartheta,xV,yV,xF,yF,xW1,yW1,xWW1,yWW1,xWWW1,yWWW1,verbose=False,log_file="decision_table1.csv")
                    if DRAWSEGMENTS or DRAWPOINTS:
                        full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, xW=xW1, yW=yW1, xWW=xWW1, yWW=yWW1, xWWW=xWWW1, yWWW=yWWW1, xF=xF, yF=yF, xV=xV, yV=yV, id0=id0, mode='draw_points_g1')
                    #protected1 = protected | isprotected1
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
                    isprotected2 = decision(QT/100,KDTREE_DIST_UPPERBOUND,limiar,limiartheta,xV,yV,xF,yF,xW2,yW2,xWW2,yWW2,xWWW2,yWWW2,verbose=False,log_file="decision_table1324.csv")
                    if DRAWSEGMENTS or DRAWPOINTS:
                        full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, xW=xW2, yW=yW2, xWW=xWW2, yWW=yWW2, xWWW=xWWW2, yWWW=yWWW2, xF=xF, yF=yF, xV=xV, yV=yV, id0=id0, mode='draw_points_g2')
                    protected = protected | isprotected2
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


##############################################
    #   select interface and add features   #
############################################## 

if True: 
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
    # Yes it s to ensure xyd follow the sequential order of vertices. We will needed for computing previous and following neighbors
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


    # if not TESTIDX:
    #     output_path = os.path.join(FOLDER, f"points-{OUTNAME}")
    #     interface_pts.to_csv(output_path, index=False, sep='\t')  

    # Save to CSV
    if SAVE_XYD: 
        VARS = ['x', 'y', 'vert_type', 'linkL', 'linkR', 'idx_vert_u',  'idx_part_u',  'interface', 'd']
        xydDT = xydDT[:, VARS]
        xydDT_df = xydDT.to_pandas()
        output_path33 = os.path.join(OUTPUT_FOLDER,FICHNAME_STEM+".csv")
        print(output_path33)
        xydDT_df.to_csv(output_path33, sep=',', index=False)

# ###############################################
# # plot
# ##############################################

# # # Show the final plot # # #
if DRAWSEGMENTS or DRAWPOINTS:
    plt.tight_layout()
    plt.show()