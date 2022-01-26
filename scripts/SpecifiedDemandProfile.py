import pandas as pd
import datetime
import functions
from collections import defaultdict

def main():
    # PURPOSE: Creates an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time   
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    seasons = functions.getFromYaml('seasons') # Dictionary holds month to season Mapping 
    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dict')['CAN'] # Canadian subregions
    years = functions.getYears()

    ###########################################
    # Calculate profile  
    ###########################################

    #generate master load dataframe
    dfLoad = functions.getLoadValues()

    #Master list to output
    #Region, fuel, timeslice, year, value
    load = []

    # Looping years here isnt super efficient. But it isnt a very long script 
    # and it make the output csv easy to read 
    for year in years:

        #filter dataframe by subregion
        for subregion, provinces in canSubregions.items(): 
            dfsubregion = pd.DataFrame() #reset df
            for province in provinces:
                dfProvince = dfLoad.loc[dfLoad['PROVINCE'] == province]
                dfsubregion = dfsubregion.append(dfProvince, ignore_index=True)

            #Get total load for year so we can normalize 
            totalLoad = dfsubregion['VALUE'].sum()

            #filter dataframe by season
            for season, months in seasons.items():
                dfSeason = pd.DataFrame() #reset df
                for month in months: 
                    dfMonth = dfsubregion.loc[dfsubregion['MONTH'] == month]
                    dfSeason = dfSeason.append(dfMonth, ignore_index=True)

                #filter dataframe by timeslice 
                for hour in range(1,25):
                    ts = season + str(hour)
                    dfFilter = dfSeason.loc[dfSeason['HOUR'] == hour]
                    profileValue = dfFilter['VALUE'].sum() / totalLoad
                    profileValue = round(profileValue, 3)
                    #pd.set_option('display.max_rows', dfFilter.shape[0]+1)
                    #print(dfFilter)

                    #Assign fuel name
                    fuelName = 'ELC' + 'CAN' + subregion + '02'

                    #save profile value 
                    load.append([continent, fuelName, ts, year, profileValue])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(load, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    dfUsa = getUsaSpecifiedDemandProfile()
    df = df.append(dfUsa)
    df.to_csv('../src/data/SpecifiedDemandProfile.csv', index=False)

def getUsaSpecifiedDemandProfile():
    # PURPOSE: Creates specifiedDeamandProfile file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    continent = functions.getFromYaml('continent')

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedDemandProfile(r,f,l,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        ts = df['TIMESLICE'].iloc[i]
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        value = round(value,3)
        outData.append([continent,fuel,ts,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    return dfOut

if __name__ == "__main__":
    main()
