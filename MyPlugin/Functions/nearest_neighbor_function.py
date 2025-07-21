##############################################
    #    Libraries       #  
##############################################
from scipy.spatial import KDTree
import datatable as dt
import pandas as pd 


##############################################
    #    Nearest Neighbor      #  
##############################################
def nearest_indices(A: dt.Frame, B: dt.Frame= None, k=1, return_distance=False) -> pd.DataFrame:
    A = A[:, ['x', 'y']]
    B = B[:, ['x', 'y']] if B is not None else A
    tree = KDTree(A)
    dist, idx = tree.query(B, k=k)
    idx = pd.DataFrame(idx, columns=[f"neighbor_{i+1}" for i in range(k)])
    dist = pd.DataFrame(dist, columns=[f"distance_{i+1}" for i in range(k)])

    if return_distance:
        return idx, dist
    return idx

