import pandas as pd
import os
import numpy as np
import functions

def main():
    # PURPOSE: Creates otoole formatted CapacityToActivityUnit CSV. Assumes all usints are in GW and PJ  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ## ASSUMES ALL CAPACITIES IN GW AND ALL ENNERGY IN PJ

    # Regions to print over
    regions = functions.openYaml().get('regions')

    techsMaster = functions.openYaml().get('techs_master')
    rnwFuels = functions.openYaml().get('rnw_fuels')
    mineFuels = functions.openYaml().get('mine_fuels')
    subregionsDict = functions.openYaml().get('subregions_dictionary')
    for key, value in subregionsDict.items():
        if key == 'CAN':
<<<<<<< HEAD
            canCountries = {key:value} # Canadian subregions
        if key == 'USA':
            usaCountries = {key:value} # American subregions
=======
            countries = {key:value} # Canadian subregions
>>>>>>> 6332b76afcb81f5b8507268c99a0acce17088b8e

    canadaAndUsaSubregions = [canCountries, usaCountries]
    technologies = functions.createTechDataframe(canadaAndUsaSubregions, techsMaster, mineFuels, rnwFuels, ['../dataSources/Trade.csv', '../dataSources/USA_Trade.csv'])
    technologiesList = technologies['VALUE'].tolist()

    ###########################################
    # CREATE FILE
    ###########################################

    #capacity to activity columns = Region, Technology, Value
    outData = []

    # unit conversion from GWyr to PJ
    # 1 GW (1 TW / 1000 GW)*(1 PW / 1000 TW)*(8760 hrs / yr)*(3600 sec / 1 hr) = 31.536
    # If 1 GW of capacity works constantly throughout the year, it produced 31.536 PJ
    capToAct = 31.536

    '''
    #populate list
    for region in regions:
        for subregion in subregions:
            for tech in pwrTechs:
                techName = 'PWR' + tech + 'CAN' + subregion + '01'
                data.append([region, techName, capToAct])
            for tech in rnwTechs:
                techName = 'RNW' + tech + 'CAN' + subregion
                data.append([region, techName, capToAct])
            for tech in minTechs:
                techName = 'MIN' + tech + 'CAN'
                data.append([region, techName, capToAct])
    '''

    #populate list
    for region in regions:
        for tech in technologiesList:
            outData.append([region, tech, capToAct])


    #write to csv
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','VALUE'])
    dfOut.to_csv('../src/data/CapacityToActivityUnit.csv', index=False)

<<<<<<< HEAD
=======
def getUsaCapToActivityUnit():
    # PURPOSE: Creates capacityToActivity file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techsMaster = functions.openYaml().get('techs_master')
    subregionsDict = functions.openYaml().get('subregions_dictionary')
    rnwFuels = functions.openYaml().get('rnw_fuels')
    mineFuels = functions.openYaml().get('mine_fuels')
    for key, value in subregionsDict.items():
        if key == 'USA':
            countries = {key:value} # American subregions

    #This one is easier to manually do...
    outData = []

    # unit conversion from GWyr to PJ
    # 1 GW (1 TW / 1000 GW)*(1 PW / 1000 TW)*(8760 hrs / yr)*(3600 sec / 1 hr) = 31.536
    # If 1 GW of capacity works constantly throughout the year, it produced 31.536 PJ
    capToAct = 31.536

    #Technologies and fuels to print over
    df = functions.createTechDataframe(countries, techsMaster, mineFuels, rnwFuels, '../dataSources/USA_Trade.csv', False)
    techs = df['VALUE'].tolist()

    #populate list
    for tech in techs:
        outData.append(['NAmerica', tech, capToAct])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION','TECHNOLOGY', 'VALUE'])
    return dfOut

>>>>>>> 6332b76afcb81f5b8507268c99a0acce17088b8e
if __name__ == "__main__":
    main()  