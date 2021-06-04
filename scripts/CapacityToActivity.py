import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted CapacityToActivityUnit.csv
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ## ASSUMES ALL CAPACITIES IN GW AND ALL ENNERGY IN PJ

    # Regions to print over
    df = pd.read_csv('../src/data/REGION.csv')
    regions = df['VALUE'].tolist()

    #Technologies to print over
    df = pd.read_csv('../src/data/TECHNOLOGY.csv')
    technologis = df['VALUE'].tolist()

    '''
    # Subregions to print over
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    subregions = df['REGION'].tolist()
    subregions = list(set(subregions)) # removes duplicates

    # PWR Techs to print over
    dfGeneration_raw = pd.read_csv('../dataSources/techList_AUTO_GENERATED.csv')
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'PWR']
    pwrTechs = dfGeneration['VALUE'].tolist()

    # RNW Techs to print over
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'RNW']
    rnwTechs = dfGeneration['VALUE'].tolist()

    # MIN Techs to print over
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'MIN']
    minTechs = dfGeneration['VALUE'].tolist()
    '''

    ###########################################
    # CREATE FILE
    ###########################################

    #capacity to activity columns = Region, Technology, Value
    data = []

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
        for tech in technologis:
            data.append([region, tech, capToAct])

    #write to csv
    dfout = pd.DataFrame(data,columns=['REGION','TECHNOLOGY','VALUE'])
    dfout.to_csv('../src/data/CapacityToActivityUnit.csv', index=False)

if __name__ == "__main__":
    main()  