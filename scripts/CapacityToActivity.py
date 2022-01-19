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
    technologies = functions.createTechDataframe(subregionsDict, techsMaster, mineFuels, rnwFuels,'../dataSources/Trade.csv')
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

    #populate list
    for region in regions:
        for tech in technologiesList:
            outData.append([region, tech, capToAct])

    #write to csv
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','VALUE'])
    dfOut.to_csv('../src/data/CapacityToActivityUnit.csv', index=False)

if __name__ == "__main__":
    main()  