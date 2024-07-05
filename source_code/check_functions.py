"""

This script contains helper functions

"""

import os

# path_check checks if a path is valid/exists

def path_check(path):
    try:
        return os.path.isfile(path) or os.path.isdir(path)
    except:
        return False

def check_string(str):
    flag_1 = False
    flag_n = False

    for i in str:
        if i.isalpha():
            flag_1 = True
            flag_n = True
        if i.isdigit():
            flag_n = True
            flag_1 = True
    
    return flag_1 and flag_n
