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
        'CanW':['BC','AB'],
        'CanMW':['SAS','MAN'],
        'CanONT':['ONT'],
        'CanQC':['QC'],
        'CanATL':['NB','NS','PEI','NL']
        }
    
    # holds baselione reserve margin for each province based on NERC
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

    #Dictionary holds month to season Mapping 
    seasons = {
        'W':[1, 2, 3],
        'SP':[4, 5, 6],
        'S':[7, 8, 9],
        'F':[10, 11, 12]}

    #For timeslicing 
    hours = range(1,25)

    ###########################################
    # ACCOUNT FOR PEAK SQUISHING
    ###########################################

    #Read in complited actual loads that have been cleaned for DST
    dfDemandRaw = pd.read_csv('../dataSources/ProvincialHourlyLoads_TimeAdjusted_AUTO_GENERATED.csv')

    #Dictionary to hold regions additional reserve margin needed. 
    peakSquishFactor = {} 

    #Filter demand dataframe for provinces in each region 
    for region, provinces in regions.items():
        dfRegion = pd.DataFrame(columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])

        #Lists to hold regional actual and max loads
        actualLoads = []
        timeSlicedLoads = []

        for province in provinces:
            dfTemp = dfDemandRaw[(dfDemandRaw['PROVINCE'] == province)]
            dfRegion = dfRegion.append(dfTemp)
        
        #The average loads are based on seasons (Jan,Feb,Mar represented as one day)
        #So we need to calculate average hourly loads for each season 
        for season, months in seasons.items():
            dfSeason = pd.DataFrame(columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])
            for month in months:
                dfTemp = dfRegion.loc[dfRegion['MONTH'] == month]
                dfSeason = dfSeason.append(dfTemp)

            #Find hourly average for each seasson 
            for hour in hours:
                dfHour = dfSeason.loc[dfSeason['HOUR']==hour]
                avgDemand = dfHour['VALUE'].mean()

                #save all timesliced loads in a list
                #dropping the season and hour mapping as reserve magin is based on year
                timeSlicedLoads.append(avgDemand)
        
        #Save all actual loads for region filtered
        actualLoads = dfRegion['VALUE'].tolist()

        #calculate peak squishing reserve margin factor
        peakTs = max(timeSlicedLoads)
        peakActual = max(actualLoads)
        peakSquish = (peakActual - peakTs) / peakActual

        #save the peak squishing factor
        #This needs to be added to every 
        peakSquishFactor[region] = peakSquish

    ##############################################
    # CALCULATE WEIGHTED BASELINE RESERVE MARGIN
    ##############################################

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

            #get regional total demand
            for province in provinces:
                totalDemand = totalDemand + dfDemand.loc[year, province]

            #weighted reserve margin based on NERC numbers
            for province in provinces:
                regionReserveMargin = regionReserveMargin + (dfDemand.loc[year, province] / totalDemand) * provincialReserveMargin[province]
            
            #add in squishing factor
            regionReserveMargin = regionReserveMargin + peakSquishFactor[region]

            #save adjusted regional reserve margin
            reserveMargin.append([region, year, regionReserveMargin])

    dfWeightedReserveMargin = pd.DataFrame(reserveMargin,columns=['REGION','YEAR','VALUE'])

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

if __name__ == "__main__":
    main()  