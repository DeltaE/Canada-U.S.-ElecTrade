import pandas as pd
import os
import numpy as np

####################################################
## ASSUMES ALL PROVINCES USE THE SAME COST VALUES ##
####################################################

def main():
    # PURPOSE: Creates otoole formatted Storage Capital Costs csv file 
    # INPUT: none
    # OUTPUT: none

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #Years to Print over
    years = range(2019,2051,1)

    #Dictory to hold storage ype and cost in M$/GW
    storages = {'TANK':11.673152}

    #List to hold all output data
    #columns = region, storage, year, value
    data = []

    for storage, cost in storages.items():
        for region in regions:
            for year in years:
                data.append([region,storage,year,cost])

    df = pd.DataFrame(data, columns=['REGION','STORAGE','YEAR','VALUE'])
    df.to_csv('../src/data/CapitalCostStorage.csv', index=False)
    



if __name__ == "__main__":
    main()