import pandas as pd
import functions
from collections import defaultdict

def main():
    # PURPOSE: Creates an otoole formatted CSV holding the specified annual demand for the model
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    continent = functions.openYaml().get('continent')
    years = functions.getYears()

    #Dictionary for subregion to province mappings
    subregions = (functions.openYaml().get('subregions_dictionary'))['CAN'] # Canadian subregions

    ###########################################
    # Calculate demand  
    ###########################################

    #Read in csv containing data
    sourceFile = '../dataSources/ProvincialAnnualDemand.csv'
    df = pd.read_csv(sourceFile, index_col=0)

    #Master list to output
    #Region, fuel, year, value
    demand = []
    
    for subregion, provinces in subregions.items(): 
        dfRegion = df[subregions[subregion]]
        sumDemand = dfRegion.loc[:,:].sum(axis=1)
        for year in years:
            fuelName = 'ELC' + 'CAN' + subregion + '02'
            value = sumDemand[year]
            value = round(value,3)
            demand.append([continent, fuelName, year, value])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(demand, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    dfUsa = getUsaSpecifiedAnnualDemand()
    df = df.append(dfUsa)
    df.to_csv('../src/data/SpecifiedAnnualDemand.csv', index=False)

def getUsaSpecifiedAnnualDemand():
    # PURPOSE: Creates specifiedAnnualDemand file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedAnnualDemand(r,f,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    continent = functions.openYaml().get('continent')

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
