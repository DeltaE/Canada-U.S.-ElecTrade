import pandas as pd
import os
import numpy as np
import functions

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
    subregions = ((functions.openYaml().get('subregions_dictionary'))['CAN']).keys() # Canadian subregions
    years = functions.getYears()

    # Tech to Fuel Mapping
    techToFuel = functions.openYaml().get('tech_to_fuel')

    # Renewable, Mining Fuels, Power Techs
    rnwFuels = functions.openYaml().get('rnw_fuels')
    minFuels = functions.openYaml().get('mine_fuels')
    pwrTechs = functions.openYaml().get('techs_master')

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
                for fuel in rnwFuels:
                    techName = 'RNW' + fuel + 'CAN' + subregion
                    fuelOut = fuel + 'CAN' + subregion
                    masterOARList.append([region, techName, fuelOut, 1, year, 1])
    
    # OAR Domestic Mining
    for region in regions:
        for year in years:
            for fuel in minFuels:
                techName = 'MIN' + fuel + 'CAN'
                fuelOut = fuel + 'CAN'
                masterOARList.append([region, techName, fuelOut, 1, year, 1])

    # IAR and OAR International Mining
    for region in regions:
        for year in years:
            for fuel in minFuels:
                techName = 'MIN' + fuel + 'INT'
                fuelIn = fuel
                fuelOut = fuel + 'INT'
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
                for fuel in pwrTechs:
                    techName = 'PWR' + fuel + 'CAN' + subregion + '01'
                    iar = dfIAR.loc[year,fuel]
                    oar = dfOAR.loc[year,fuel]
                    fuelName = techToFuel[fuel]
                    # if has international imports
                    if fuelName in minFuels:
                        inFuelModeOne = fuelName + 'CAN'
                        inFuelModeTwo = fuelName + 'INT'
                        outFuel = 'ELC' + 'CAN' + subregion + '01'
                        masterIARList.append([region, techName, inFuelModeOne, 1, year, iar])
                        masterIARList.append([region, techName, inFuelModeTwo, 2, year, iar])
                        masterOARList.append([region, techName, outFuel, 1, year, oar])
                        masterOARList.append([region, techName, outFuel, 2, year, oar])
                    # edge case of storage. This is super hacked together... will need to update
                    elif fuel == 'P2G' or fuel == 'FCL':
                        # P2G will only have input activity ratio 
                        if fuel == 'P2G':
                            inFuel = 'ELC' + 'CAN' + subregion + '02'
                            outFuel = 'HY2' + 'CAN' + subregion + '01'
                            masterIARList.append([region, techName, inFuel, 1, year, iar])
                            masterOARList.append([region, techName, outFuel, 1, year, 0])
                        # P2G will only have output activity ratio 
                        elif fuel == 'FCL':
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
    dfInputUsa = getUsaInputActivityRatio()
    dfInputOut = dfInputOut.append(dfInputUsa)
    dfInputOut.to_csv(f'../src/data/InputActivityRatio.csv', index=False)
    dfOutputOut = pd.DataFrame(masterOARList,columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    dfOutputUsa = getUsaOutputActivityRatio()
    dfOutputOut = dfOutputOut.append(dfOutputUsa)
    dfOutputOut.to_csv(f'../src/data/OutputActivityRatio.csv', index=False)

def getUsaOutputActivityRatio():
    # PURPOSE: Creates outputActivityRatio file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    subregions = (functions.openYaml().get('subregions_dictionary'))['USA'] # American subregions
    region = functions.openYaml().get('regions')[0]

    #Fuels that have international trade options
    intFuel = functions.openYaml().get('mine_fuels')
    rnwFuel = functions.openYaml().get('rnw_fuels')

    #holds output data
    outData = []

    #year to print over
    years = functions.getYears()

    #renewables
    for year in years:
        for rawFuel in rnwFuel:
            for subregion in subregions:
                techName = 'RNW' + rawFuel + 'USA' + subregion
                fuel = rawFuel + 'USA' + subregion 
                outData.append([region, techName, fuel, 1, year, 1])

    #mining USA
    for year in years:
        for rawFuel in intFuel:
            techName = 'MIN' + rawFuel + 'USA'
            fuel = rawFuel + 'USA'
            outData.append([region, techName, fuel, 1, year, 1])

    # OAR for PWRTRN technologies
    for subregion in subregions:
        for year in years:
            techName = 'PWR' + 'TRN' + 'USA' + subregion
            fuel = 'ELC' + 'USA' + subregion + '02'
            outData.append([region, techName, fuel, 1, year, 1])

    # OAR for PWR technologies
    for year in years:
        for subregion in subregions:
            for tech in techMap:
                techName = 'PWR' + techMap[tech] + 'USA' + subregion + '01'
                fuel = 'ELC' + 'USA' + subregion + '01'
                outData.append([region, techName, fuel, 1, year, 1])
                if techMap[tech] in intFuel:
                    outData.append([region, techName, fuel, 2, year, 1])

<<<<<<< HEAD
    #OAR for transmission
    dfTrn = pd.read_csv('../dataSources/USA_Trade.csv')
    for year in functions.getYears():
        for i in range(len(dfTrn)):
            techName = dfTrn.iloc[i]['TECHNOLOGY']
            outFuel = dfTrn.iloc[i]['OUTFUEL']
            oar = dfTrn.iloc[i]['OAR']
            mode = dfTrn.iloc[i]['MODE']
            outData.append([region, techName, outFuel, mode, year, oar])

=======
>>>>>>> main
    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

def getUsaInputActivityRatio():
    # PURPOSE: Creates inputActivityRatio file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'InputActivityRatio(r,t,f,m,y)')
    techMap = functions.openYaml().get('usa_tech_map')
    subregions = (functions.openYaml().get('subregions_dictionary'))['USA'] # American subregions
    inputFuelMap = functions.openYaml().get('tech_to_fuel')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)

    df = dfFiltered
    df.reset_index()    

    #Fuels that have international trade options
    intFuel = functions.openYaml().get('mine_fuels')

    #holds output data
    outData = []

    region = functions.openYaml().get('regions')[0]

    #map data
    for i in range(len(df)):
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['INPUTACTIVITYRATIO'].iloc[i]
        value = round(value, 3)
        fuelMapped = inputFuelMap[techMapped]

        #check if tech will operate on two modes of operation
        if fuelMapped in intFuel:
            fuel = fuelMapped + 'USA'
            outData.append([region,tech,fuel,1,year,value])
            fuel = fuelMapped + 'INT'
            outData.append([region,tech,fuel,2,year,value])
        else:
            fuel = fuelMapped + 'USA' + df['REGION'].iloc[i]
            outData.append([region,tech,fuel,1,year,value])

    # IAR for PWRTRN technologies
    for subregion in subregions:
        for year in functions.getYears():
            techName = 'PWR' + 'TRN' + 'USA' + subregion
            fuelIn = 'ELC' + 'USA' + subregion + '01'
            outData.append([region, techName, fuelIn, 1, year, 1])
<<<<<<< HEAD
    
    #IAR for transmission
    dfTrn = pd.read_csv('../dataSources/USA_Trade.csv')
    for year in functions.getYears():
        for i in range(len(dfTrn)):
            techName = dfTrn.iloc[i]['TECHNOLOGY']
            inFuel = dfTrn.iloc[i]['INFUEL']
            iar = dfTrn.iloc[i]['IAR']
            mode = dfTrn.iloc[i]['MODE']
            outData.append([region, techName, inFuel, mode, year, iar])
=======
>>>>>>> main

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()