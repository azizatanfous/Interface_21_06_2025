##############################################
    #    Libraries       #  
##############################################
import numpy as np

##############################################
    #    Functions       #  
##############################################

# Retrieves the k-th neighbor coordinates and its previous (FFF) and next (FF) neighbors.
def get_neighbors(mat_df, idx, idxneigh_func, in_type, x_col='x', y_col='y', feat_col='idx_feat'):
    """
    Input:
    mat_df : pandas.DataFrame
    idx : array-like (Indices of the k-th neighbor)
    idxneigh_func : function
    in_type : str : type ("flam", "urb")
    x_col : str ('x')
    y_col : str  ('y')
    feat_col : str ('idx_feat')
    Output:Tuple
    """
    x = mat_df.loc[idx, x_col].to_numpy()
    y = mat_df.loc[idx, y_col].to_numpy()
    # Get next (FF) and previous (FFF) neighbors
    res = idxneigh_func(mat=mat_df, idxviz=idx, IN=in_type)
    x_next = mat_df.loc[res['idxnext'], x_col].to_numpy()
    y_next = mat_df.loc[res['idxnext'], y_col].to_numpy()
    x_prev = mat_df.loc[res['idxprev'], x_col].to_numpy()
    y_prev = mat_df.loc[res['idxprev'], y_col].to_numpy()
    idx_feat = mat_df.loc[idx, feat_col].to_numpy() # Retrieve the closest non-protected feature index
    return x, y, x_next, y_next, x_prev, y_prev, idx_feat


#  adjust coordinates
def adjust_coordinates(x1, y1, x2, y2, x_ref, y_ref):
    delta_x = x1 - x2
    delta_y = y1 - y2
    delta = delta_x**2 + delta_y**2
    delta = np.nan_to_num(delta, nan=0)
    lambda_ = np.where(delta > 0, ((x_ref - x2) * delta_x + (y_ref - y2) * delta_y) / delta, 1)
    lambda_ = np.where((lambda_ <= 0) | (lambda_ >= 1), 1, lambda_)
    x2_adj = lambda_ * x1 + (1 - lambda_) * x2
    y2_adj = lambda_ * y1 + (1 - lambda_) * y2
    return x2_adj, y2_adj
