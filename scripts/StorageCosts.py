import pandas as pd
import os
import numpy as np
import functions

####################################################
## ASSUMES ALL PROVINCES USE THE SAME COST VALUES ##
####################################################

def main():
    # PURPOSE: Creates an otoole formatted CapitalCostStorage CSV AND OperationalLifeStorage CSV
    # INPUT: none
    # OUTPUT: none

    # Parameters to print over
    regions = functions.openYaml().get('regions')
    subregions = (functions.openYaml().get('subregions_dictionary')).keys()
    years = functions.getYears()

    #Read in master list of technologies and get storage names
    dfGeneration_raw = pd.read_csv('../dataSources/techList_AUTO_GENERATED.csv')
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'STO']
    storages = dfGeneration['VALUE'].tolist()
    if not storages:
        df = pd.DataFrame(columns=['REGION','STORAGE','YEAR','VALUE'])
        df.to_csv('../src/data/CapitalCostStorage.csv', index=False)
        return

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
    df.to_csv('../src/data/CapitalCostStorage.csv', index=False)
    



if __name__ == "__main__":
    main()