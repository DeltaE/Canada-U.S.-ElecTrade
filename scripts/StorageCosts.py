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
    df = pd.read_csv('../src/data/Canada/REGION.csv')
    regions = df['VALUE'].tolist()

    # Subregions to print over
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    subregions = df['REGION'].tolist()
    subregions = list(set(subregions)) # removes duplicates

    #Years to Print over
    dfYears = pd.read_csv('../src/data/Canada/YEAR.csv')
    years = dfYears['VALUE'].tolist()

    #Read in master list of technologies and get storage names
    dfGeneration_raw = pd.read_csv('../dataSources/techList_AUTO_GENERATED.csv')
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'STO']
    storages = dfGeneration['VALUE'].tolist()

    #Dictory to hold storage ype and cost in M$/GW
    storageCosts = {'TNK':11.673152}

    ##############################
    ## Populate data
    ##############################

    #columns = region, storage, year, value
    data = []

    for region in regions:
        for year in years:
            for subregion in subregions:
                for storage in storages:
                    stoName = 'STO' + storage + 'CAN' + subregion
                    cost = storageCosts[storage]
                    data.append([region,stoName,year,cost])

    df = pd.DataFrame(data, columns=['REGION','STORAGE','YEAR','VALUE'])
    df.to_csv('../src/data/Canada/CapitalCostStorage.csv', index=False)
    



if __name__ == "__main__":
    main()