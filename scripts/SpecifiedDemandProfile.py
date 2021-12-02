import pandas as pd
import datetime
import functions
from collections import defaultdict
import usa_data_functions

def main():
    # PURPOSE: Creates an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time   
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary holds month to season Mapping 
    seasons = functions.openYaml().get('seasons')

    # Parameters to print over
    regions = functions.openYaml().get('regions')
    subregions = functions.openYaml().get('subregions_dictionary')
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
    for region in regions:
        for year in years:

            #filter dataframe by subregion
            for subregion, provinces in subregions.items(): 
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
                        load.append([region, fuelName, ts, year, profileValue])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(load, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    dfUsa = usa_data_functions.getSpecifiedDemandProfile()
    df = df.append(dfUsa)
    df.to_csv('../src/data/SpecifiedDemandProfile.csv', index=False)

if __name__ == "__main__":
    main()
