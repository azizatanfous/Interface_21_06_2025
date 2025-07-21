##############################################
    #    Library       #  
##############################################
import os
##############################################
    #    Main Function       #  
##############################################
def get_project_directories():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..')) # one level up
    input_folder = os.path.join(project_root, "Data")
    output_folder = os.path.join(project_root, "Output")
    
    return input_folder, output_folder
