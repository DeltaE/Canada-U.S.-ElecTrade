import pandas as pd
import os
import numpy as np
import datetime
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted ReserveMargin, ReserveMarginTagFuel, and 
    #          ReserveMarginTagTechnology CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

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

    #Years to Print over
    dfYears = pd.read_csv('../src/data/Canada/YEAR.csv')
    years = dfYears['VALUE'].tolist()
    
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
    #techTags = ['HYD','BIO','CCG','CTG','URN','COA','COC','WND', 'SPV']
    techTags = ['HYD','BIO','CCG','CTG','URN','COA','COC']

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
    for subregion, provinces in subregions.items():
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
        peakSquishFactor[subregion] = peakSquish

    ##############################################
    # CALCULATE WEIGHTED BASELINE RESERVE MARGIN
    ##############################################

    #Read in csv containing data
    sourceFile = '../dataSources/ProvincialAnnualDemand.csv'
    dfDemand = pd.read_csv(sourceFile, index_col=0)

    # List to hold region reserve margins
    #Region, year, value
    reserveMarginRaw = []

    for subregion, provinces in subregions.items():
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
            regionReserveMargin = regionReserveMargin + peakSquishFactor[subregion]

            #save adjusted regional reserve margin
            reserveMarginRaw.append([subregion, year, regionReserveMargin])

    #To include reserve margin in osemosys global naming scheme, we:
    # Gave a value of 1 for all regions and years of reserve margin 
    # assigned the regional reserve margin value to ELCCAN<subregion>01 in reserve margin tag fuel
    # assign a value of one to all relevant PWR<technology>CAN<subregion>01

    #Reserve Margin = Region, year, value
    reserveMargin = []
    for region in regions:
        for year in years:
            reserveMargin.append([region, year, 1])

    #reserve margin Tag Fuel = Region, Fuel, Year, Value
    reserveMarginTagFuel = []
    for region in regions:
        for i in range(len(reserveMarginRaw)):
            fuelName = 'ELC' + 'CAN' + reserveMarginRaw[i][0] + '01'
            year = reserveMarginRaw[i][1]
            rm = reserveMarginRaw[i][2]
            rm = round(rm,3)
            reserveMarginTagFuel.append([region, fuelName, year, rm])
    
    #reserve margin Tag Technology = Region, Technology, Year, Value
    reserveMarginTagTech = []
    for region in regions:
        for subregion in subregions:
            for year in years:
                for tech in techTags:
                    techName = 'PWR' + tech + 'CAN' +subregion + '01'
                    reserveMarginTagTech.append([region, techName, year, 1])

    #write out all files
    dfReserveMargin = pd.DataFrame(reserveMargin,columns=['REGION','YEAR','VALUE'])
    dfReserveMargin.to_csv('../src/data/Canada/ReserveMargin.csv', index=False)

    dfReserveMarginFuel = pd.DataFrame(reserveMarginTagFuel,columns=['REGION','FUEL','YEAR','VALUE'])
    dfReserveMarginFuel.to_csv('../src/data/Canada/ReserveMarginTagFuel.csv', index=False)

    dfReserveMarginTech = pd.DataFrame(reserveMarginTagTech,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfReserveMarginTech.to_csv('../src/data/Canada/ReserveMarginTagTechnology.csv', index=False)

    # Reference code before switching over to osemosys gloabl naming 
    '''
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

    '''

if __name__ == "__main__":
    main()  