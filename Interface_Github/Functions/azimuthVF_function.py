##############################################
    #    Library     #  
##############################################
import numpy as np

##############################################
    #    Main Function       #  
##############################################

def azimuthVF(xV, yV, xF, yF):
    dx = xF - xV
    dy = yF - yV
    d = np.vectorize(complex)(dx, dy)  
    az = ((2 * np.pi + np.pi / 2 - np.angle(d)) % (2 * np.pi)) * 180 / np.pi
    is_same = (dx == 0) & (dy == 0)
    az[is_same] = 360  # points are identical
    return az



