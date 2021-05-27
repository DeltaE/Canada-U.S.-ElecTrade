import pandas as pd
import os
import numpy as np

##############################################################
## ASSUMES ALL REGIONS USE THE SAME OPERATIONAL LIFE VALUES ##
##############################################################

def main():
    # PURPOSE: Creates otoole formatted Storage Operational Life csv file 
    # INPUT: none
    # OUTPUT: none

    #Regions to print over 
    regions = ['CanW','CanMW','CanONT','CanQC','CanATL']

    #Dictory to hold storage ype and op life in years
    storages = {'TANK':30}

    #List to hold all output data
    #columns = region, storage, value
    data = []

    for storage, years in storages.items():
        for region in regions:
            data.append([region,storage,years])

    df = pd.DataFrame(data, columns=['REGION','STORAGE','VALUE'])
    df.to_csv('../src/data/OperationalLifeStorage.csv', index=False)
    
if __name__ == "__main__":
    main()