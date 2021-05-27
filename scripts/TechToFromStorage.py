import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted TechnologyTo/FromStorage CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ## WRITES TO MODE_OF_OPERATION 1

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #TechnologyToStorage (Technology, Storage)
    techToStorage = {
        'P2G':'TANK',
    }

    #TechnologyToStorage (Technology, Storage)
    techFromStorage = {
        'FC':'TANK',
    }

    ###########################################
    # Write files
    ###########################################

    #list to hold all output values
    #columns = region, technology, storage, mode, value
    toStorageData = []
    fromStorageData = []

    #print all values 
    for region in regions:
        for tech,storage in techToStorage.items():
            toStorageData.append([region, tech, storage, 1, 1])
        for tech,storage in techFromStorage.items():
            fromStorageData.append([region, tech, storage, 1, 1])
    
    #write tech to storage
    dfOut = pd.DataFrame(toStorageData,columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
    dfOut.to_csv('../src/data/TechnologyToStorage.csv', index=False)

    #write tech from storage
    dfOut = pd.DataFrame(fromStorageData,columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
    dfOut.to_csv('../src/data/TechnologyFromStorage.csv', index=False)

if __name__ == "__main__":
    main()