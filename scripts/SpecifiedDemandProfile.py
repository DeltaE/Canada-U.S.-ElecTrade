import pandas as pd
import os
import numpy as np
import datetime
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted SpecifiedDemandProfile csv file 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary for region to province mappings
    regions = defaultdict(list)

    # Read in regionalization file 
    df = pd.read_csv('../dataSources/Regionalization.csv')
    for i in range(len(df)):    
        region = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        regions[region].append(province)

    #Dictionary holds month to season Mapping 
    seasons = {
        'W':[1, 2, 3],
        'SP':[4, 5, 6],
        'S':[7, 8, 9],
        'F':[10, 11, 12]}

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Calculate profile  
    ###########################################

    #generate master load dataframe
    dfLoad = getLoadValues()

    #save load dataframe for use in other scripts
    dfLoad.to_csv('../dataSources/ProvincialHourlyLoads_TimeAdjusted_AUTO_GENERATED.csv', index=False)

    #Master list to output
    #Region, fuel, timeslice, year, value
    load = []

    # Looping years here isnt super inefficient. But it isnt a very long script 
    # and it make the output csv easy to read 
    for year in years:

        #filter dataframe by region
        for region, provinces in regions.items(): 
            dfRegion = pd.DataFrame() #reset df
            for province in provinces:
                dfProvince = dfLoad.loc[dfLoad['PROVINCE'] == province]
                dfRegion = dfRegion.append(dfProvince, ignore_index=True)

            #Get total load for year so we can normalize 
            totalLoad = dfRegion['VALUE'].sum()

            #filter dataframe by season
            for season, months in seasons.items():
                dfSeason = pd.DataFrame() #reset df
                for month in months: 
                    dfMonth = dfRegion.loc[dfRegion['MONTH'] == month]
                    dfSeason = dfSeason.append(dfMonth, ignore_index=True)

                #filter dataframe by timeslice 
                for hour in range(1,25):
                    ts = season + str(hour)
                    dfFilter = dfSeason.loc[dfSeason['HOUR'] == hour]
                    profileValue = dfFilter['VALUE'].sum() / totalLoad
                    #pd.set_option('display.max_rows', dfFilter.shape[0]+1)
                    #print(dfFilter)

                    #save profile value 
                    load.append([region, 'ELC', ts, year, profileValue])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(load, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    df.to_csv('../src/data/SpecifiedDemandProfile.csv', index=False)

###########################################
# Extra Functions 
###########################################

def getLoadValues():
    # PURPOSE: Takes hourly load value excel sheet and converts it into a master df
    # INPUT: none
    # OUTPUT: Dataframe with the columns: Province, Month, Day, Hour, Load Value 
    #Dictionary to hold timezone shifting values 
    timeZone = {
        'BC':0,
        'AB':1,
        'SAS':2,
        'MAN':2,
        'ONT':3,
        'QC':3,
        'NB':4,
        'NL':4,
        'NS':4,
        'PEI':4}

    #Read in all provinces
    sourceFile = '../dataSources/ProvincialHourlyLoads.xlsx'
    sheets = pd.read_excel(sourceFile, sheet_name=None)

    #Will store output information with the columns...
    #Province, month, hour, load [MW]
    data = []

    #Loop over sheets and store in a master list 
    for province, sheet in sheets.items():
        dateList = sheet['Date'].tolist()
        hourList = sheet['HOUR (LOCAL)'].tolist()
        loadList = sheet['LOAD [MW]'].tolist()

        #loop over list and break out month, day, hour from date
        for i in range(len(dateList)):
            dateFull = dateList[i]
            date = datetime.datetime.strptime(dateFull, '%Y-%m-%d')

            #Shift time values to match BC time (ie. Shift 3pm Alberta time back one hour, so all timeslices represent the asme time)
            hourAdjusted = int(hourList[i]) - timeZone[province]
            if hourAdjusted < 1:
                hourAdjusted = hourAdjusted + 24

            #Save data
            data.append([province, date.month, date.day, hourAdjusted, loadList[i]])

    #process daylight savings time values 
    data = daylightSavings(data)

    #dataframe to output 
    dfOut = pd.DataFrame(data,columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])
    return dfOut


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
                print(f'hour averaged for {inData[i][0]} on month {inData[i][1]}, day {inData[i][2]}, hour {inData[i][3]}')

    #Remove the rows in reverse order so we are counting starting from the start of the list
    for i in reversed(rowsToRemove):
        inData.pop(i)

    #check if hour is missing a load
    for i in range(len(inData)-1):
        #first condition if data marks the load as zero 
        if (inData[i][4] < 1): 
            inData[i][4] = inData[i-1][4]
            print(f'hour modified for {inData[i][0]} on month {inData[i][1]}, day {inData[i][2]}, hour {inData[i][3]}')
        #second adn third conditions for if data just skips the time step 
        elif (int(inData[i+1][3]) - int(inData[i][3]) == 2) or (int(inData[i][3]) - int(inData[i+1][3]) == 22):
            rowsToAdd.append(i)
            print(f'hour added for {inData[i][0]} on month {inData[i][1]}, day {inData[i][2]}, hour {inData[i][3]}')

    #Add the rows in reverse order so we are counting starting from the start of the list
    for i in reversed(rowsToAdd):
        rowAfter = inData[i+1]
        newHour = rowAfter[3] - 1
        newRow = [rowAfter[0], rowAfter[1], rowAfter[2], newHour, rowAfter[4]]
        inData.insert(i, newRow)

    return inData

if __name__ == "__main__":
    main()
