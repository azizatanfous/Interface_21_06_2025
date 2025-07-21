##############################################
    #    Libraries       #  
##############################################
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
##############################################
    #    Main Function       #  
##############################################
def full_plot_function(ax, flammable_path, urban_path, mat_urb_df, mat_flam_df, BOX, 
                                 x0=None, y0=None, d=None,  
                                 xFF=None, xF=None, xFFF=None, yFF=None, yF=None, yFFF=None, valid_idxF=None,
                                 xFback=None, yFback=None, id0=None, 
                                 xW=None, yW=None, xWW=None, yWW=None, xWWW=None, yWWW=None, 
                                 xV=None, yV=None, protected=None, idxFviz=None, mode='all'):

    # Load and crop geospatial files only once
    flammable_gdf, urban_gdf = None, None
    if mode in ['all', 'plot_cropped_background_layout']:
        flammable_gdf = gpd.read_file(flammable_path).clip([BOX['xmin'], BOX['ymin'], BOX['xmax'], BOX['ymax']])
        urban_gdf = gpd.read_file(urban_path).clip([BOX['xmin'], BOX['ymin'], BOX['xmax'], BOX['ymax']])

        # Crop data frames to the bounding box
        mat_urb_df_cropped = mat_urb_df[(mat_urb_df['x'].between(BOX['xmin'], BOX['xmax'])) & 
                                        (mat_urb_df['y'].between(BOX['ymin'], BOX['ymax']))]
        mat_flam_df_cropped = mat_flam_df[(mat_flam_df['x'].between(BOX['xmin'], BOX['xmax'])) & 
                                          (mat_flam_df['y'].between(BOX['ymin'], BOX['ymax']))]

        # Plot areas and vertices
        flammable_gdf.plot(ax=ax, color='red', alpha=0.5, edgecolor='black', label='Flammable Areas')
        urban_gdf.plot(ax=ax, color='blue', alpha=0.5, edgecolor='black', label='Urban Areas')
        
        ax.scatter(mat_flam_df_cropped['x'], mat_flam_df_cropped['y'], facecolors='none', edgecolors='darkred', s=90, marker='^', label='Flammable Vertices')
        ax.scatter(mat_urb_df_cropped['x'], mat_urb_df_cropped['y'], facecolors='none', edgecolors='darkblue', s=50, marker='s', label='Urban Vertices')

    # Plot reference circle and filtered points within it
    if mode in ['all', 'add_filtered_points'] and x0 is not None and y0 is not None and d is not None:
        circle = Circle((x0, y0), d, color='yellow', fill=False, linestyle='--', linewidth=2, label=f'Circle with radius d={d}')
        ax.add_patch(circle)
        distance_from_center = (mat_urb_df['x'] - x0)**2 + (mat_urb_df['y'] - y0)**2
        points_in_circle = distance_from_center < d**2
        ax.scatter(mat_urb_df.loc[points_in_circle, 'x'], mat_urb_df.loc[points_in_circle, 'y'], color='lightgreen', marker='o', s=30, label='Filtered Points within Circle')
    
    if mode in ['all', 'plot_valid_idxF'] and valid_idxF is not None and len(valid_idxF) > 0:
            for i, idx in enumerate(valid_idxF):
                if not np.isnan(idx):  
                    x, y = xF[i], yF[i]
                    ax.scatter(x, y, color='purple', marker='x', s=40, label='Valid Flammable Neighbor' if i == 0 else "")
                    ax.text(x + 0.01, y + 0.01, f"{int(idx)}", fontsize=8, ha='center', color='black', verticalalignment='bottom')

    # Plot segments only if they lie within the circle
    if mode in ['all', 'plot_segments'] and xFF is not None and xF is not None and xFFF is not None:
        distances = [(x - x0)**2 + (y - y0)**2 for x, y in zip(xFF, yFF)]
        segments_within_circle = [i for i, dist in enumerate(distances) if dist < d**2]
        for i in segments_within_circle:
            ax.plot([xFF[i], xF[i], xFFF[i]], [yFF[i], yF[i], yFFF[i]], color='brown', linewidth=2)

    # Plot labels for selected points
    if mode in ['all', 'plot_labels'] and xFback is not None and yFback is not None and id0 is not None:
        ax.text(xFback[id0], yFback[id0], "F", fontsize=8, ha='right', color='#1f77b4')
        if xFF is not None and yFF is not None:
            ax.text(xFF[id0], yFF[id0], "FF", fontsize=8, ha='center', color='#ff7f0e')
        if xFFF is not None and yFFF is not None:
            ax.text(xFFF[id0], yFFF[id0], "FFF", fontsize=8, ha='left', color='#2ca02c')
        ax.text(xFback[id0], yFback[id0], f"id0: {id0}", fontsize=8, ha='center', color='#d62728')

    # Proportional size points
    if mode in ['all', 'plot_points'] and idxFviz is not None:
        ax.scatter(xF, yF, s=(2 + idxFviz) * 20, color='darkgreen', linewidth=2, facecolors='none', edgecolors='darkgreen', alpha=0.6)
        ax.set_xlim(x0 - d, x0 + d)
        ax.set_ylim(y0 - d, y0 + d)

    # Draw individual points and final segments based on protection status
    if mode in ['all', 'draw_points_g1'] and id0 is not None:
        ax.text(xW[id0], yW[id0], "W1", fontsize=10, color="black", verticalalignment='bottom')
        ax.scatter(xF[id0], yF[id0], s=100, color="green", edgecolors="black", marker="o", label="F")
        
    if mode in ['all', 'draw_points_g2'] and id0 is not None:
        ax.text(xW[id0], yW[id0], "W2", fontsize=10, color="black", verticalalignment='bottom')
        ax.scatter(xF[id0], yF[id0], s=100, color="yellow", edgecolors="black", marker="o", label="F")

    if mode in ['all', 'draw_last_segments'] and id0 is not None:
        linestyle = ['-', '--', '-.', ':'][idxFviz % 4]
        color = "black" if protected[id0] else "red"
        ax.plot([xV[id0], xF[id0]], [yV[id0], yF[id0]],id0,color=color, linestyle=linestyle)
        

