import shutil, subprocess, os

def CheckLibrary(lib):
    lib_path = shutil.which(lib)
    if lib_path:
        return True
    return False