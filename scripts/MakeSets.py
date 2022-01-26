import pandas as pd
import functions
from itertools import islice

def main():
    # PURPOSE: Creates Tech and Fuel sets. Writes our files that are referenced by other scripts
    # INPUT: none
    # OUTPUT: none

    ####################################
    ## MODEL PARAMETERS
    ####################################

    continent = functions.getFromYaml('continent')
    emissions = functions.getFromYaml('emissions')
    techsMaster = functions.getFromYaml('techs_master')
    rnwFuels = functions.getFromYaml('rnw_fuels')
    mineFuels = functions.getFromYaml('mine_fuels')
    stoTechs = functions.getFromYaml('sto_techs')
    subregions = functions.getFromYaml('regions_dict')
    years = functions.getYears()

    ####################################
    ## CREATE STANDARD SETS
    ####################################

    # Years set
    dfOut = pd.DataFrame(years,columns=['VALUE'])
    dfOut.to_csv('../src/data/YEAR.csv', index=False)

    #Regions set
    dfOut = pd.DataFrame([continent], columns=['VALUE'])
    dfOut.to_csv('../src/data/REGION.csv', index=False)

    # Emissions set
    dfOut = pd.DataFrame(emissions, columns=['VALUE'])
    dfOut.to_csv('../src/data/EMISSION.csv', index=False)

    ####################################
    ## CREATE STORAGE SET
    ####################################

    #get storages for each region 
    stoList = getSTO(subregions, stoTechs)

    dfOut = pd.DataFrame(stoList, columns=['VALUE'])
    dfOut.to_csv('../src/data/STORAGE.csv', index=False)

    ####################################
    ## CREATE TECHNOLOGY SET
    ####################################

    df = functions.createTechDataframe(subregions, techsMaster, mineFuels, rnwFuels, '../dataSources/Trade.csv')
    df.to_csv('../src/data/TECHNOLOGY.csv', index=False)

    ####################################
    ## CREATE FUEL SET
    ####################################

    df = functions.createFuelDataframe(subregions, rnwFuels, mineFuels)
    df.to_csv('../src/data/FUEL.csv', index=False)

####################################
## Extra Functions
####################################

def getSTO(subregions, storages):
    # PURPOSE: Creates storage names
    # INPUT:   subregions = Dictionary holding Country and regions 
    #          ({CAN:{WS:[...], ...} USA:[NY:[...],...]})
    # OUTPUT:  outList =  List of all the STO names

    # list to hold technologies
    outList = []

    if not storages:
        return storages

    # Loop to create all technology names
    for region, subregions in subregions.items():
        for subregion in subregions['CAN']:
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