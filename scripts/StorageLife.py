import pandas as pd
import functions

##############################################################
## ASSUMES ALL REGIONS USE THE SAME OPERATIONAL LIFE VALUES ##
##############################################################

def main():
    # PURPOSE: Creates otoole formatted Storage Operational Life csv file 
    # INPUT: none
    # OUTPUT: none

    # Regions to print over
    regions = functions.initializeRegions()

    # Subregions to print over
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    subregions = df['REGION'].tolist()
    subregions = list(set(subregions)) # removes duplicates

    #Read in master list of technologies and get storage names
    dfGeneration_raw = pd.read_csv('../dataSources/techList_AUTO_GENERATED.csv')
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'STO']
    storages = dfGeneration['VALUE'].tolist()

    if not storages:
        df = pd.DataFrame(columns=['REGION','STORAGE','VALUE'])
        df.to_csv('../src/data/Canada/OperationalLifeStorage.csv', index=False)
        return

    #Dictory to hold storage ype and op life in years
    storageLife = {'TNK':30}

    #List to hold all output data
    #columns = region, storage, value
    data = []

    for region in regions:
        for subregion in subregions:
            for storage in storages:
                stoName = 'STO' + storage + 'CAN' + subregion
                life = storageLife[storage]
                data.append([region,stoName,life])

    df = pd.DataFrame(data, columns=['REGION','STORAGE','VALUE'])
    df.to_csv('../src/data/Canada/OperationalLifeStorage.csv', index=False)
    
if __name__ == "__main__":
    main()