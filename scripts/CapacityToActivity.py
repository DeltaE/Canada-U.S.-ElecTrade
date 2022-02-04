import pandas as pd
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
    continent = functions.getFromYaml('continent')
    techsMaster = functions.getFromYaml('techs_master')
    rnwFuels = functions.getFromYaml('rnw_fuels')
    mineFuels = functions.getFromYaml('mine_fuels')
    subregions = functions.getFromYaml('regions_dict')

    technologies = functions.createTechDataframe(subregions, techsMaster, mineFuels, rnwFuels,'../dataSources/Trade.csv')
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
    for tech in technologiesList:
        outData.append([continent, tech, capToAct])

    #write to csv
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','VALUE'])
    dfOut.to_csv('../src/data/CapacityToActivityUnit.csv', index=False)

if __name__ == "__main__":
    main()  