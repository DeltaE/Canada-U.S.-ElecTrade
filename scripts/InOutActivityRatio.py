import pandas as pd
import os
import numpy as np
import functions
import usa_data_functions

def main():
    # PURPOSE: Creates otoole formatted InputActivityRatio AND OutputActivityRatio CSVs  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ###EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1

    # Parameters to print over
    regions = functions.openYaml().get('regions')
    subregions = functions.openYaml().get('subregions_list')
    years = functions.getYears()

    # Tech to Fuel Mapping
    techToFuel = functions.openYaml().get('tech_to_fuel')

    ###########################################
    # Get Min and Rnw techs
    ###########################################

    #Read in master list of technologies
    dfGeneration_raw = pd.read_csv('../dataSources/techList_AUTO_GENERATED.csv')

    #Populate techs by type dictionary
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'RNW']
    rnwTechs = dfGeneration['VALUE'].tolist()
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'MIN']
    minTechs = dfGeneration['VALUE'].tolist()
    dfGeneration = dfGeneration_raw.loc[dfGeneration_raw['GENERATION'] == 'PWR']
    pwrTechs = dfGeneration['VALUE'].tolist()

    ###########################################
    # IAR and OAR of One
    ###########################################

    #coumns = Region, Tech, Fuel, Mode, Year, Value
    masterIARList = []
    masterOARList = []

    # OAR Renweable Generations
    for region in regions:
        for year in years:
            for subregion in subregions:
                for tech in rnwTechs:
                    techName = 'RNW' + tech + 'CAN' + subregion
                    fuelOut = tech + 'CAN' + subregion
                    masterOARList.append([region, techName, fuelOut, 1, year, 1])
    
    # OAR Domestic Mining
    for region in regions:
        for year in years:
            for tech in minTechs:
                techName = 'MIN' + tech + 'CAN'
                fuelOut = tech + 'CAN'
                masterOARList.append([region, techName, fuelOut, 1, year, 1])

    # IAR and OAR International Mining
    for region in regions:
        for year in years:
            for tech in minTechs:
                techName = 'MIN' + tech + 'INT'
                fuelIn = tech
                fuelOut = tech + 'INT'
                masterIARList.append([region, techName, fuelIn, 1, year, 1])
                masterOARList.append([region, techName, fuelOut, 1, year, 1])

    # IAR and OAR for PWRTRN technologies
    for region in regions:
        for year in years:
            for subregion in subregions:
                techName = 'PWR' + 'TRN' + 'CAN' + subregion
                fuelIn = 'ELC' + 'CAN' + subregion + '01'
                fuelOut = 'ELC' + 'CAN' + subregion + '02'
                masterIARList.append([region, techName, fuelIn, 1, year, 1])
                masterOARList.append([region, techName, fuelOut, 1, year, 1])

    # IAR and OAR for TRN technologies
    df = pd.read_csv('../dataSources/Trade.csv')
    for region in regions:
        for year in years:
            for i in range(len(df)):
                techName = df.iloc[i]['TECHNOLOGY']
                inFuel = df.iloc[i]['INFUEL']
                outFuel = df.iloc[i]['OUTFUEL']
                iar = df.iloc[i]['IAR']
                oar = df.iloc[i]['OAR']
                mode = df.iloc[i]['MODE']
                masterIARList.append([region, techName, inFuel, mode, year, iar])
                masterOARList.append([region, techName, outFuel, mode, year, oar])

    # IAR and OAR for RNW PWR technologies
    dfIAR = pd.read_csv('../dataSources/InputActivityRatioByTechnology.csv', index_col=0)
    dfOAR = pd.read_csv('../dataSources/OutputActivityRatioByTechnology.csv', index_col=0)
    for region in regions:
        for year in years:
            for subregion in subregions:
                for tech in pwrTechs:
                    techName = 'PWR' + tech + 'CAN' + subregion + '01'
                    iar = dfIAR.loc[year,tech]
                    oar = dfOAR.loc[year,tech]
                    fuelName = techToFuel[tech]
                    # if has international imports
                    if fuelName in minTechs:
                        inFuelModeOne = fuelName + 'CAN'
                        inFuelModeTwo = fuelName + 'INT'
                        outFuel = 'ELC' + 'CAN' + subregion + '01'
                        masterIARList.append([region, techName, inFuelModeOne, 1, year, iar])
                        masterIARList.append([region, techName, inFuelModeTwo, 2, year, iar])
                        masterOARList.append([region, techName, outFuel, 1, year, oar])
                        masterOARList.append([region, techName, outFuel, 2, year, oar])
                    # edge case of storage. This is super hacked together... will need to update
                    elif tech == 'P2G' or tech == 'FCL':
                        # P2G will only have input activity ratio 
                        if tech == 'P2G':
                            inFuel = 'ELC' + 'CAN' + subregion + '02'
                            outFuel = 'HY2' + 'CAN' + subregion + '01'
                            masterIARList.append([region, techName, inFuel, 1, year, iar])
                            masterOARList.append([region, techName, outFuel, 1, year, 0])
                        # P2G will only have output activity ratio 
                        elif tech == 'FCL':
                            inFuel = 'HY2' + 'CAN' + subregion + '01'
                            outFuel = 'ELC' + 'CAN' + subregion + '02'
                            masterIARList.append([region, techName, inFuel, 1, year, 0])
                            masterOARList.append([region, techName, outFuel, 1, year, oar])
                    # Renewables
                    else:
                        inFuel = fuelName + 'CAN' + subregion
                        outFuel = 'ELC' + 'CAN' + subregion + '01'
                        masterIARList.append([region, techName, inFuel, 1, year, iar])
                        masterOARList.append([region, techName, outFuel, 1, year, oar])

    #write IAR and OAR to files 
    dfInputOut = pd.DataFrame(masterIARList,columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    dfInputUsa = usa_data_functions.getSpecifiedAnnualDemand()
    dfInputOut = dfInputOut.append(dfInputUsa)
    dfInputOut.to_csv(f'../src/data/InputActivityRatio.csv', index=False)
    dfOutputOut = pd.DataFrame(masterOARList,columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    dfOutputUsa = usa_data_functions.getSpecifiedAnnualDemand()
    dfOutputOut = dfOutputOut.append(dfOutputUsa)
    dfOutputOut.to_csv(f'../src/data/OutputActivityRatio.csv', index=False)

if __name__ == "__main__":
    main()