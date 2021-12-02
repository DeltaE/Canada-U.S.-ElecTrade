#####################################
## This file is for retrieving all USA information
#####################################

import pandas as pd
import functions

def getVariableCost():
    # PURPOSE: Creates variableCost file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    inputFuelMap = functions.openYaml().get('tech_to_fuel')
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'VariableCost(r,t,m,y)')

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
    intFuel = ['GAS','COA','URN']

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        mode = 1
        value = df['VARIABLECOST'].iloc[i]
        value = round(value, 3)
        outData.append([region,tech,mode,year,value])
        #checks if need to write value for mode 2
        if inputFuelMap[techMapped] in intFuel:
            mode = 2
            outData.append([region,tech,mode,year,value])

    #Get trade costs
    dfCosts = pd.read_csv('../dataSources/USA_Trade.csv')

    #Cost data only populated on mode 1 data rows
    dfCosts = dfCosts.loc[dfCosts['MODE'] == 1]

    # get list of all the technologies
    techList = dfCosts['TECHNOLOGY'].tolist()

    #Regions to print over
    regions = ['NAmerica']

    #cost types to get data for
    costType = ['Variable O&M', 'Fuel']

    #populate data
    for region in regions:
        for tech in techList:

            #remove all rows except for our technology
            dfCostsFiltered = dfCosts.loc[dfCosts['TECHNOLOGY']==tech]
            dfCostsFiltered.reset_index()

            #reset costs
            trnCost = 0

            #get costs
            for cost in costType:
                trnCost = trnCost + float(dfCostsFiltered[cost].iloc[0])
            trnCost = round(trnCost, 3)

            #save same value for all years 
            for year in range(2019,2051):
                outData.append([region,tech,1,year,trnCost])
                outData.append([region,tech,2,year,trnCost])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

def getTotalAnnualMaxCapacity():
    # PURPOSE: Creates TotalAnnualMaxCapacity header data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    dfOut = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getSpecifiedDemandProfile():
    # PURPOSE: Creates specifiedDeamandProfile file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedDemandProfile(r,f,l,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        ts = df['TIMESLICE'].iloc[i]
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        value = round(value,3)
        outData.append([region,fuel,ts,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    return dfOut

def getSpecifiedAnnualDemand():
    # PURPOSE: Creates specifiedAnnualDemand file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedAnnualDemand(r,f,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        value = round(value,3)
        outData.append([region,fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    return dfOut

def getRETagTechnology():
    # PURPOSE: Creates RETagTechnology file from USA data
    # INPUT:   none
    # OUTPUT:  dfOut = dataframe to be written to a csv

    dummy, regions, emissions, techsMaster, rnwTechs, mineTechs, stoTechs, subregions = functions.initializeCanadaUsaModelParameters('USA')

    #easier to do this one manually 
    techs = ['HYD','WND','BIO','SPV']
    years = range(2019,2051)

    outData = []

    for year in years:
        for subregion in subregions['USA']:
            for tech in techs:
                region = 'NAmerica'
                techName = 'PWR' + tech + 'USA' + subregion + '01'
                outData.append([region, techName, year, 1])

    # create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut