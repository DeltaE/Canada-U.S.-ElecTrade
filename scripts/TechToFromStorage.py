import pandas as pd
import functions

def main():
    # PURPOSE: Creates otoole formatted CSVs holding TechnologyToStorage and TechnologyFromStorage  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dict')['CAN'].keys() # Canadian subregions
    storages = functions.getFromYaml('sto_techs')
    
    if not storages:
        dfOut = pd.DataFrame(columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
        dfOut.to_csv('../src/data/TechnologyToStorage.csv', index=False)
        dfOut.to_csv('../src/data/TechnologyFromStorage.csv', index=False)
        return

    #TechnologyToStorage (Technology, Storage)
    techToStorage = {
        'TNK':'P2G'
    }

    #TechnologyToStorage (Technology, Storage)
    techFromStorage = {
        'TNK':'FCL'
    }

    ###########################################
    # Write files
    ###########################################

    #list to hold all output values
    #columns = region, technology, storage, mode, value
    toStorageData = []
    fromStorageData = []

    #print all values 
    for subregion in canSubregions:
        for storage in storages:
            #Tech to storage
            techName = 'PWR' + techToStorage[storage] + 'CAN' + subregion + '01'
            storageName = 'STO' + storage + 'CAN' + subregion
            toStorageData.append([continent, techName, storageName, 1.0, 1])
            #Tech from storage
            techName = 'PWR' + techFromStorage[storage] + 'CAN' + subregion + '01'
            storageName = 'STO' + storage + 'CAN' + subregion
            fromStorageData.append([continent, techName, storageName, 1.0, 1])
    
    #write tech to storage
    dfOut = pd.DataFrame(toStorageData,columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
    dfOut.to_csv('../src/data/TechnologyToStorage.csv', index=False)

    #write tech from storage
    dfOut = pd.DataFrame(fromStorageData,columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
    dfOut.to_csv('../src/data/TechnologyFromStorage.csv', index=False)

if __name__ == "__main__":
    main()