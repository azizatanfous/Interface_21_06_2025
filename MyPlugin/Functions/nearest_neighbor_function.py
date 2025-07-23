##############################################
    #    Libraries       #  
##############################################
from scipy.spatial import KDTree
import datatable as dt
import pandas as pd 
import numpy as np


##############################################
    #    Nearest Neighbor      #  
##############################################
def nearest_indices(A: dt.Frame, B: dt.Frame= None, k=1, return_distance=False,KDTREE_DIST_UPPERBOUND=1000,bigN=10**6) -> pd.DataFrame:
    A = A[:, ['x', 'y']]
    B = B[:, ['x', 'y']] if B is not None else A
    tree = KDTree(A)
    dist, idx = tree.query(B, k=k, distance_upper_bound=KDTREE_DIST_UPPERBOUND)
    MyInvalidIndex = 0  # or any value you prefer
    idx[idx == tree.n] = MyInvalidIndex
    idx = pd.DataFrame(idx, columns=[f"neighbor_{i+1}" for i in range(k)])
    if return_distance:
        dist[dist == np.inf] = bigN
        dist = pd.DataFrame(dist, columns=[f"distance_{i+1}" for i in range(k)])
        return idx, dist
    else:
        return idx