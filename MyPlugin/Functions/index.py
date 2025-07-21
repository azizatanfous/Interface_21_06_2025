##############################################
    #    Libraries       #  
##############################################
import pandas as pd
import numpy as np


##############################################
    #    The idxneigh function     #  
##############################################

def idxneigh(mat, idxviz, IN):
    """
    Determines the previous and next neighbor indices .

    Parameters:
    mat (DataFrame): A Pandas DataFrame containing indexed geometric data.
    idxviz (array-like): A list or array of indices for which neighbors are determined.
    IN (str): A suffix indicating whether the data is 'urban' ('u') or 'flammable' ('f').

    Returns:
    dict: A dictionary with two keys:
        - 'idxprev': List of previous neighbor indices.
        - 'idxnext': List of next neighbor indices.
    """
    colpart = f"idx_part_{IN}"
    
    idxnext = []
    idxprev = []
    
    for idx in idxviz:
        if np.isnan(idx):  # Preserve NaN in idxviz
            idxnext.append(np.nan)
            idxprev.append(np.nan)
            continue
        
        idx = int(idx)  
        if idx < 0 or idx >= mat.shape[0]:
            idxnext.append(np.nan)
            idxprev.append(np.nan)
            continue

        next_idx = idx + 1 if idx < mat.shape[0] - 1 else mat.shape[0] - 1
        prev_idx = idx - 1 if idx > 0 else 0

        current_part = mat.iloc[idx][colpart]
        

        if prev_idx != idx and mat.iloc[prev_idx][colpart] == current_part:
            idxprev.append(prev_idx)
        else:
            idxprev.append(idx)

        if next_idx != idx and mat.iloc[next_idx][colpart] == current_part:
            idxnext.append(next_idx)
        else:
            idxnext.append(idx)
    
    return {'idxprev': idxprev, 'idxnext': idxnext}


