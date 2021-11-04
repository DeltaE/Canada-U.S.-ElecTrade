import pandas as pd
import functions

##############################################################
## ASSUMES ALL REGIONS USE THE SAME OPERATIONAL LIFE VALUES ##
##############################################################

def main():
    # PURPOSE: Creates otoole formatted Storage Operational Life csv file 
    # INPUT: none
    # OUTPUT: none

    # Parameters to print over
    regions = functions.initializeRegions()
    subregions = functions.initializeSubregionsAsList()
    storages = functions.initializeStorages()

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