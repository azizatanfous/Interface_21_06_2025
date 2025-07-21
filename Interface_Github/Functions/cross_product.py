##############################################
    #    Main Function       #  
##############################################

# Cross product between (P1-P2) and (P3-P4)
def crossprod(x1, y1, x2, y2, x3, y3, x4, y4):
    return (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)

