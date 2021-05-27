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

    #Regions to print over 
    regions = ['CanW','CanMW','CanONT','CanQC','CanATL']

    #Years to Print over
    years = range(2019,2051,1)

    #Dictory to hold storage ype and cost in $/GW
    storages = {'TANK':11673152}

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