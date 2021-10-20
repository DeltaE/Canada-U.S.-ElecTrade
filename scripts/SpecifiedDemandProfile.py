import pandas as pd
import datetime
from functions import getLoadValues
from collections import defaultdict

def main():
    # PURPOSE: Creates an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time   
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary holds month to season Mapping 
    seasons = {
        'W':[1, 2, 12],
        'SP':[3, 4, 5],
        'S':[6, 7, 8],
        'F':[9, 10, 11]}

    #Years to Print over
    dfYears = pd.read_csv('../src/data/Canada/YEAR.csv')
    years = dfYears['VALUE'].tolist()

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/Canada/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #Dictionary for subregion to province mappings
    subregions = defaultdict(list)

    # Read in regionalization file to get provincial seperation
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    for i in range(len(df)):    
        subregion = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        subregions[subregion].append(province)

    ###########################################
    # Calculate profile  
    ###########################################

    #generate master load dataframe
    dfLoad = functions.getLoadValues()

    ###########################################
    # DEPRECATED
    # #save load dataframe for use in other scripts
    # dfLoad.to_csv('../dataSources/ProvincialHourlyLoads_TimeAdjusted_AUTO_GENERATED.csv', index=False)
    ###########################################

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
    df.to_csv('../src/data/Canada/SpecifiedDemandProfile.csv', index=False)

###########################################
# Extra Functions 
###########################################

def daylightSavings(inData):
# PURPOSE: Processess a input list to accout for daylight savings 
#          1) For a load of zero - the load at the same time in the previous day is used
#          2) For a double load - uses same load as previous adjacent hour  
# INPUT: list with the columns: Province, Month, Day, Hour, Load Value
# OUTPUT: list with the columns: Province, Month, Day, Hour, Load Value

############################################################################
# ASSUMES DAYLIGHT SAVINGS DAY IS NOT IN THE FIRST OR LAST DAY of the list #
############################################################################

    #Split this into two for loop for user clarity when reading output file. The faster option will 
    #be to just append the added values to the end of the list in the first list

    #keep track of what rows to remove data for 
    rowsToRemove = []
    rowsToAdd = []

    for i in range(len(inData) - 1):
        #check if one hour is the same as the next 
        if inData[i][3] == inData[i+1][3]:
            #Check that regions are the same 
            if(inData[i][0] == inData[i+1][0]): 
                average = (inData[i][4] + inData[i+1][4]) / 2
                inData[i+1][4] = average
                rowsToRemove.append(i)
                #print(f'hour averaged for {inData[i][0]} on month {inData[i][1]}, day {inData[i][2]}, hour {inData[i][3]}')

    #Remove the rows in reverse order so we are counting starting from the start of the list
    for i in reversed(rowsToRemove):
        inData.pop(i)

    #check if hour is missing a load
    for i in range(len(inData)-1):
        #first condition if data marks the load as zero 
        if (inData[i][4] < 1): 
            inData[i][4] = inData[i-1][4]
            #print(f'hour modified for {inData[i][0]} on month {inData[i][1]}, day {inData[i][2]}, hour {inData[i][3]}')
        #second adn third conditions for if data just skips the time step 
        elif (int(inData[i+1][3]) - int(inData[i][3]) == 2) or (int(inData[i][3]) - int(inData[i+1][3]) == 22):
            rowsToAdd.append(i)
            #print(f'hour added for {inData[i][0]} on month {inData[i][1]}, day {inData[i][2]}, hour {inData[i][3]}')

    #Add the rows in reverse order so we are counting starting from the start of the list
    for i in reversed(rowsToAdd):
        rowAfter = inData[i+1]
        newHour = rowAfter[3] - 1
        newRow = [rowAfter[0], rowAfter[1], rowAfter[2], newHour, rowAfter[4]]
        inData.insert(i, newRow)

    return inData

if __name__ == "__main__":
    main()
