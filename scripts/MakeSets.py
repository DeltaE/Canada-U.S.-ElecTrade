import pandas as pd
import functions

def main():
    # PURPOSE: Creates Tech and Fuel sets. Writes our files that are referenced by other scripts
    # INPUT: none
    # OUTPUT: none

    ####################################
    ## MODEL PARAMETERS
    ####################################

    regions = functions.openYaml().get('regions')
    emissions = functions.openYaml().get('emissions')
    techsMaster = functions.openYaml().get('techs_master')
    rnwTechs = functions.openYaml().get('rnw_techs')
    mineTechs = functions.openYaml().get('mine_techs')
    stoTechs = functions.openYaml().get('sto_techs')
    years = functions.getYears()
    canCountries = functions.getRegionDictionary('CAN')
    usaCountries = functions.getRegionDictionary('USA')

    ####################################
    ## CREATE STANDARD SETS
    ####################################

    # Years set
    dfOut = pd.DataFrame(years,columns=['VALUE'])
    dfOut.to_csv('../src/data/YEAR.csv', index=False)

    #Regions set
    dfOut = pd.DataFrame(regions, columns=['VALUE'])
    dfOut.to_csv('../src/data/REGION.csv', index=False)

    # Emissions set
    dfOut = pd.DataFrame(emissions, columns=['VALUE'])
    dfOut.to_csv('../src/data/EMISSION.csv', index=False)

    ####################################
    ## CREATE STORAGE SET
    ####################################

    #get storages for each region 
    stoList = getSTO(canCountries, stoTechs)

    dfOut = pd.DataFrame(stoList, columns=['VALUE'])
    dfOut.to_csv('../src/data/STORAGE.csv', index=False)

    ####################################
    ## CREATE TECHNOLOGY SET
    ####################################

    canadaDfOut = functions.createTechDataframe(canCountries, techsMaster, mineTechs, rnwTechs, '../dataSources/Trade.csv', True)
    usaDfOut = functions.createTechDataframe(usaCountries, techsMaster, mineTechs, rnwTechs, '../dataSources/USA_Trade.csv', False)
    df = canadaDfOut.append(usaDfOut)
    df.to_csv('../src/data/TECHNOLOGY.csv', index=False)

    ####################################
    ## CREATE FUEL SET
    ####################################

    canadaDfOut = functions.createFuelDataframe(canCountries, rnwTechs, mineTechs, True)
    usaDfOut = functions.createFuelDataframe(usaCountries, rnwTechs, mineTechs, False)
    df = canadaDfOut.append(usaDfOut)
    df.to_csv('../src/data/FUEL.csv', index=False)

####################################
## Extra Functions
####################################

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

'''
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
'''

if __name__ == "__main__":
    main()  