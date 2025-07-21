##############################################
    #    Main Function       #  
##############################################
def ftype(d, D):
    return (d == 0).astype(int) + \
           ((d > 0) & (d <= 100)).astype(int) * 2 + \
           ((d > 100) & (d <= 250)).astype(int) * 3 + \
           ((d > 250) & (d <= D)).astype(int) * 4 + \
           (d > D).astype(int) * 5