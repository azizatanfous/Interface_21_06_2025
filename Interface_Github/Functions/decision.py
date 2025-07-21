##############################################
    #    Libraries       #  
##############################################
import numpy as np
import pandas as pd

bigN = 10**6
##############################################
    #    Import Functions       #  
##############################################
from Main_Script.constants import * 
from Functions.dot_product import * 
from Functions.cross_product import * 

##############################################
    #    Main Function     #  
##############################################

# is V protected from F by (WWW,W,WW)?
def decision(Q,KDTREE_DIST_UPPERBOUND, limiar, limiartheta, xV, yV, xF, yF, xW, yW, xWW, yWW, xWWW, yWWW, verbose=False, log_file="decision_table.csv"):
    """
    Determines if a flammable point is protected based on distances, angles, and whether
    the flammable-to-urban line intersects ANY urban edge.
    """
    # Distance calculations
    d2VF = (xV - xF)**2 + (yV - yF)**2
    d2VW = (xV - xW)**2 + (yV - yW)**2
    d2WF = (xW - xF)**2 + (yW - yF)**2

    sqrt_d2VW = np.sqrt(d2VW)
    sqrt_d2WF = np.sqrt(d2WF)
    sqrt_d2VF = np.sqrt(d2VF)

    # Angle calculation
    dot = (xW - xV) * (xF - xV) + (yW - yV) * (yF - yV)
    thetaV = np.full_like(dot, limiartheta)

    cond = (
        ~np.isnan(xV) & ~np.isnan(xF) & ~np.isnan(xW) &
        np.greater(d2VW , 0) & np.greater(d2VF , 0) & np.less_equal(dot**2 , d2VW * d2VF)
    )
    thetaV[cond] = np.degrees(np.arccos(dot[cond] / np.sqrt(d2VW[cond] * d2VF[cond])))

    # Triangle perimeter condition
    perimeter = sqrt_d2VW + sqrt_d2WF + sqrt_d2VF
    Q_condition = (
        np.greater(sqrt_d2VW , perimeter * Q) &
        np.greater(sqrt_d2WF , perimeter * Q) &
        np.greater(sqrt_d2VF , perimeter * Q)
    )

    protedge_next = (
        (np.less(crossprod(xW,yW,xWW,yWW,xW,yW,xF,yF)*crossprod(xW,yW,xWW,yWW,xW,yW,xV,yV) , -smallN)  | 
        np.less_equal(np.abs(crossprod(xW,yW,xWW,yWW,xW,yW,xF,yF)), smallN )) & 
        np.less(crossprod(xV,yV,xF,yF,xV,yV,xW,yW)*crossprod(xV,yV,xF,yF,xV,yV,xWW,yWW), -smallN)
    )
    np.nan_to_num(protedge_next, nan=0).astype(bool)

    protedge_prev = (
        (np.less(crossprod(xW,yW,xWWW,yWWW,xW,yW,xF,yF)*crossprod(xW,yW,xWWW,yWWW,xW,yW,xV,yV) , -smallN)  | 
        np.less_equal(np.abs(crossprod(xW,yW,xWWW,yWWW,xW,yW,xF,yF)), smallN )) & 
        np.less(crossprod(xV,yV,xF,yF,xV,yV,xW,yW)*crossprod(xV,yV,xF,yF,xV,yV,xWWW,yWWW), -smallN)
    )
    np.nan_to_num(protedge_prev, nan=0).astype(bool)


    # Logical conditions
    
    condition_artifact = (xF == bigN) & (yF == bigN)
    condition_intersects = protedge_next | protedge_prev
    condition_valid_distances = ~np.isnan(d2VF) & ~np.isnan(d2VW) & ~np.isnan(d2WF)
    condition_positive_distances = np.greater(d2VW , 0) & np.greater(d2VF , 0) & np.greater(d2WF , 0)
    condition_threshold = np.less(sqrt_d2VW + sqrt_d2WF , limiar * sqrt_d2VF)
    condition_angle = np.less(thetaV , limiartheta)
    condition_closer_urban = np.greater_equal(d2VF ,d2VW) & np.greater_equal(d2VF, d2WF)
    condition_triangle = Q_condition
    condition_outside_region = np.greater(d2VF , 2 * KDTREE_DIST_UPPERBOUND**2)

    # Final protection decision
    result = (
        condition_intersects |condition_artifact|
        (
            ~condition_outside_region &
            condition_valid_distances &
            condition_positive_distances &
            condition_threshold &
            condition_angle &
            condition_closer_urban &
            condition_triangle
        )
    )
    return result

    if False:
        # Log result
        table = pd.DataFrame({
            "xF": xF, "yF": yF,
            "xV": xV, "yV": yV,
            "xW": xW, "yW": yW,
            "xWW": xWW, "yWW": yWW,
            "xWWW": xWWW, "yWWW": yWWW,
            "Artifact Condition": condition_artifact,
            "Intersects Urban Edge": condition_intersects,
            "Valid Distances": condition_valid_distances,
            "Positive Distances": condition_positive_distances,
            "Threshold Condition": condition_threshold,
            "Angle Condition": condition_angle,
            "Closer Urban Condition": condition_closer_urban,
            "Triangle Condition": condition_triangle,
            "Outside Region Condition": condition_outside_region,
            "Final Decision": result
        })
        table.to_csv(log_file, index=False)
        if verbose:
            print(f"Results logged to {log_file}")

        


