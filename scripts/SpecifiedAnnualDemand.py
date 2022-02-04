import pandas as pd
import functions
from collections import defaultdict

def main():
    # PURPOSE: Creates an otoole formatted CSV holding the specified annual demand for the model
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Writing Demand Files 
    ###########################################

    dfUsa = getUsaSpecifiedAnnualDemand()
    dfCan = getCanSpecifiedAnnualDemand()

    df = pd.DataFrame(dfCan, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    df = df.append(dfUsa)
    df.to_csv('../src/data/SpecifiedAnnualDemand.csv', index=False)

def getCanSpecifiedAnnualDemand():
    # PURPOSE: Creates specifiedAnnualDemand file from Canadian data
    # INPUT:   N/A
    # OUTPUT:  demand = master list to be appended to dataframe

    # Parameters to print over
    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dict')['CAN'] # Canadian subregions
    years = functions.getYears()

    ###########################################
    # Calculate demand  
    ###########################################

    #Read in csv containing data
    sourceFile = '../dataSources/ProvincialAnnualDemand.csv'
    df = pd.read_csv(sourceFile, index_col=0)

    #Master list to output
    #Region, fuel, year, value
    demand = []
    
    for subregion, provinces in canSubregions.items(): 
        dfProvinces = df[canSubregions[subregion]]
        sumDemand = dfProvinces.loc[:,:].sum(axis=1)
        for year in years:
            fuelName = 'ELC' + 'CAN' + subregion + '02'
            value = sumDemand[year]
            value = round(value,3)
            demand.append([continent, fuelName, year, value])
    
    return demand

def getUsaSpecifiedAnnualDemand():
    # PURPOSE: Creates specifiedAnnualDemand file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    continent = functions.getFromYaml('continent')

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedAnnualDemand(r,f,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        value = round(value,3)
        outData.append([continent,fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    return dfOut

if __name__ == "__main__":
    main()
