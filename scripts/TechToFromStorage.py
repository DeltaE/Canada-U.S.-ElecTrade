import pandas as pd

def main():
    # PURPOSE: Creates otoole formatted TechnologyTo/FromStorage CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Regions to print over
    df = pd.read_csv('../src/data/Canada/REGION.csv')
    regions = df['VALUE'].tolist()

    # Subregions to print over
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    subregions = df['REGION'].tolist()
    subregions = list(set(subregions)) # removes duplicates

    #Read in master list of technologies and get storage names
    dfGeneration_raw = pd.read_csv('../dataSources/techList_AUTO_GENERATED.csv')
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'STO']
    storages = dfGeneration['VALUE'].tolist()
    if not storages:
        dfOut = pd.DataFrame(columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
        dfOut.to_csv('../src/data/Canada/TechnologyToStorage.csv', index=False)
        dfOut.to_csv('../src/data/Canada/TechnologyFromStorage.csv', index=False)
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
    for region in regions:
        for subregion in subregions:
            for storage in storages:
                #Tech to storage
                techName = 'PWR' + techToStorage[storage] + 'CAN' + subregion + '01'
                storageName = 'STO' + storage + 'CAN' + subregion
                toStorageData.append([region, techName, storageName, 1.0, 1])
                #Tech from storage
                techName = 'PWR' + techFromStorage[storage] + 'CAN' + subregion + '01'
                storageName = 'STO' + storage + 'CAN' + subregion
                fromStorageData.append([region, techName, storageName, 1.0, 1])
    
    #write tech to storage
    dfOut = pd.DataFrame(toStorageData,columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
    dfOut.to_csv('../src/data/Canada/TechnologyToStorage.csv', index=False)

    #write tech from storage
    dfOut = pd.DataFrame(fromStorageData,columns=['REGION','TECHNOLOGY','STORAGE', 'MODE_OF_OPERATION','VALUE'])
    dfOut.to_csv('../src/data/Canada/TechnologyFromStorage.csv', index=False)

if __name__ == "__main__":
    main()