import os
import csv

def Access_BreakDown_CSV(filename:str):
    currentDir = os.getcwd()
    parentDir = os.path.dirname(currentDir)
    
    breakdownFile = os.path.join(parentDir, filename)
    return breakdownFile

def Read_BreakDowns(filename:str):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            pass
    