##############################################
    #    Main Function       #  
##############################################
def create_bounding_box(x0,y0, d):
    
    bounding_box = {
        'xmin': x0 - d,
        'xmax': x0 + d,
        'ymin': y0 - d,
        'ymax': y0 + d
    }
    
    return bounding_box # Return a  dictionary
