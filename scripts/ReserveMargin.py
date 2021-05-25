import pandas as pd
import os
import numpy as np
import datetime

def main():
    # PURPOSE: Creates otoole formatted ReserveMargin, ReserveMarginTagFuel, and 
    #          ReserveMarginTagTechnology CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Region Dictionary
    regions = {
        'W':['BC','AB'],
        'MW':['SAS','MAN'],
        'ME':['ONT','NB'],
        'E':['QC','NS','PEI','NL']}
    
    # holds the reserve margin for each province
    # 10 percent for hydro dominated provinces
    # 15 percent for thermal dominated regions 
    provincialReserveMargin = {
        'BC':1.10,
        'AB':1.15,
        'SAS':1.15,
        'MAN':1.10,
        'ONT':1.15,
        'QC':1.10,
        'NB':1.15,
        'NL':1.10,
        'NS':1.15,
        'PEI':1.15}

    #Years to Print over
    years = range(2019,2051,1)

    # List of fuels to tag
    fuelTag = ['ELC']

    # List of technologies to tag
    techTag = ['HYD','BIO','NGCC','NGCT','NUC','CL','CLCCS','FC']

    ###########################################
    # CALCULATE WEIGHTED RESERVE MARGIN
    ###########################################

    #Read in csv containing data
    sourceFile = '../dataSources/ProvincialAnnualDemand.csv'
    dfDemand = pd.read_csv(sourceFile, index_col=0)

    # List to hold region reserve margins
    #Region, year, value
    reserveMargin = []

    for region, provinces in regions.items():
        for year in years: 
            totalDemand = 0
            regionReserveMargin = 0
            for province in provinces:
                totalDemand = totalDemand + dfDemand.loc[year, province]
            for province in provinces:
                regionReserveMargin = regionReserveMargin + (dfDemand.loc[year, province] / totalDemand) * provincialReserveMargin[province]
            reserveMargin.append([region, year, regionReserveMargin])

    dfWeightedReserveMargin = pd.DataFrame(reserveMargin,columns=['REGION','YEAR','VALUE'])

    '''
    # Region, year, value
    reserveMargin = []

    #Account for peak squishing 
    #Find max hourly demand value 
    dfHourlyLoad = getLoadValues()
    for region, provinces in regions.items():
        for year in years: 
            dfRegion = pd.DataFrame(columns=['PROVINCE','MONTH','DAY','HOUR','VALUE'])
            #filter load by province
            for province in provinces: 
                dfTemp = dfHourlyLoad.loc[dfHourlyLoad['PROVINCE']==province]
                dfRegion = dfRegion.append(dfTemp)
            #calculate reserve margin based on peak
            maxLoad = dfRegion['VALUE'].max()
            averageLoad = dfRegion['VALUE'].mean()
            inputReserveMargin = dfWeightedReserveMargin.loc[
                (dfWeightedReserveMargin['REGION'] == region) & 
                (dfWeightedReserveMargin['YEAR'] == year)]
            inputReserveMargin.reset_index()
            #calculate adjusted reserve margin
            reserveMarginAdjusted = (maxLoad / averageLoad) * inputReserveMargin['VALUE'].iloc[0]
            reserveMargin.append([region,year,reserveMarginAdjusted])
    '''

    #reserve margin Tag Fuel = Region, Fuel, Year, Value
    reserveMarginTagFuel = []

    #reserve margin Tag Technology = Region, Technology, Year, Value
    reserveMarginTagTech = []

    #populate lists 
    for region, rm in regions.items():
        for year in years:
            for fuel in fuelTag:
                reserveMarginTagFuel.append([region, fuel, year, 1])
            for tech in techTag:
                reserveMarginTagTech.append([region, tech, year, 1])

    #write to csvs
    dfReserveMargin = pd.DataFrame(reserveMargin,columns=['REGION','YEAR','VALUE'])
    dfReserveMargin.to_csv('../src/data/ReserveMargin.csv', index=False)

    dfReserveMarginFuel = pd.DataFrame(reserveMarginTagFuel,columns=['REGION','FUEL','YEAR','VALUE'])
    dfReserveMarginFuel.to_csv('../src/data/ReserveMarginTagFuel.csv', index=False)

    dfReserveMarginTech = pd.DataFrame(reserveMarginTagTech,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfReserveMarginTech.to_csv('../src/data/ReserveMarginTagTechnology.csv', index=False)


###########################################
# Extra Functions 
###########################################

def getLoadValues():
    # PURPOSE: Takes hourly load value excel sheet and converts it into a mater df
    # INPUT: none
    # OUTPUT: Dataframe with the columns: Province, Month, Day, Hour, Load Value 
    # Dictionary to hold timezone shifting values 
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