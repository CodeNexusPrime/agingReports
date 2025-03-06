import os

def Access_BreakDown_CSV(filename:str):
    currentDir = os.getcwd()
    parentDir = os.path.dirname(currentDir)
    
    breakdownFile = os.path.join(parentDir, filename)
    return breakdownFile
    