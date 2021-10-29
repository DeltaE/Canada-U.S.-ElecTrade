import pandas as pd
import functions

def main():
    # PURPOSE: Creates Tech and Fuel sets. Writes our files that are referenced by other scripts
    # INPUT: none
    # OUTPUT: none

    ####################################
    ## MODEL PARAMETERS
    ####################################

    years, regions, emissions, techsMaster, rnwTechs, mineTechs, stoTechs, countries = functions.initializeCanadaUsaModelParameters('CAN')

    #######################################
    ## CREATE TECH LISTS FOR OTHER SCRIPTS
    #######################################
    
    data = functions.createTechLists(techsMaster, rnwTechs, mineTechs, stoTechs)

    dfGenerationType = pd.DataFrame(data, columns=['GENERATION','VALUE'])
    dfGenerationType.to_csv('../dataSources/techList_AUTO_GENERATED.csv', index = False)

    ####################################
    ## CREATE STANDARD SETS
    ####################################

    # Years set
    dfOut = pd.DataFrame(years,columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/YEAR.csv', index=False)

    #Regions set
    dfOut = pd.DataFrame(regions, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/REGION.csv', index=False)

    # Emissions set
    dfOut = pd.DataFrame(emissions, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/EMISSION.csv', index=False)

    ####################################
    ## CREATE STORAGE SET
    ####################################

    #get storages for each region 
    stoList = getSTO(countries, stoTechs)

    dfOut = pd.DataFrame(stoList, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/STORAGE.csv', index=False)

    ####################################
    ## CREATE TECHNOLOGY SET
    ####################################

    functions.createTechnologySet(countries, techsMaster, mineTechs, rnwTechs, '../dataSources/Trade.csv', '../src/data/Canada/TECHNOLOGY.csv', 1)

    ####################################
    ## CREATE FUEL SET
    ####################################

    functions.createFuelSet(countries, rnwTechs, mineTechs, '../src/data/Canada/FUEL.csv', 1)

    ####################################
    ## Extra Functions
    ####################################

def getHY2fuels(regions):
    # PURPOSE: Creates Hydrogen Fuel names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the ELC Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            fuelName = 'HY2' + region + subregion + '01'
            outList.append(fuelName)
    
    # Return list of hydrogen fuels
    return outList

def getSTO(regions, storages):
    # PURPOSE: Creates storage names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the STO names

    # list to hold technologies
    outList = []

    if not storages:
        return storages

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for storage in storages:
                storageName = 'STO' + storage + region + subregion
                outList.append(storageName)
    
    # Return list of hydrogen fuels
    return outList

if __name__ == "__main__":
    main()  