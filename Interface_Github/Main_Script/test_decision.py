import numpy as np
import pandas as pd
import os, sys

# Get the absolute path of the parent directory (Interface_Github)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from constants import * 
from Functions.decision import * 
from Functions.dot_product import * 
from Functions.cross_product import * 

xV=np.array([0,0,0,0,0,0,0,0,0])
yV=np.array([0,0,0,5,5,5,20,20,20])
xF=np.array([10,10,10,10,10,10,10,10,10])
yF=np.array([0,5,10,0,5,10,0,5,10])
xW=np.array([5,5,5,5,5,5,5,5,5])
yW=np.array([-2,3,8,-2,3,8,-2,3,8])
xWW=np.array([5,5,5,5,5,5,5,5,5])
yWW=np.array([-7,-2,3,-7,-2,3,-7,-2,3])
xWWW=np.array([5,5,5,5,5,5,5,5,5])
yWWW=np.array([3,8,13,3,8,13,3,8,13])

# Q should be a parameter
print(decision(QT,KDTREE_DIST_UPPERBOUND, limiar, limiartheta, xV, yV, xF, yF, xW, yW, xWW, yWW, xWWW, yWWW, verbose=False, log_file="decision_table_test.csv"))