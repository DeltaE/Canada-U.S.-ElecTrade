import pandas as pd
import os
import numpy as np
import datetime
import functions
import usa_data_functions
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted ReserveMargin, ReserveMarginTagFuel, and 
    #          ReserveMarginTagTechnology CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    regions = functions.openYaml().get('regions')
    subregions = functions.openYaml().get('subregions_dictionary')
    seasons = functions.openYaml().get('seasons')
    years = functions.getYears()
    
    # holds baseline reserve margin for each province based on NERC
    # 10 percent for hydro dominated provinces
    # 15 percent for thermal dominated regions 
    PROVINCIAL_RESERVE_MARGIN = {
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

    # List of fuels to tag
    # fuelTag = ['ELC']

    # List of technologies to tag
    techTags = functions.openYaml().get('techs_master')
    variableTechs = functions.openYaml().get('variable_techs')
    # Remove the non-dispachable techs from techTags
    techTags = [x for x in techTags if x not in variableTechs]

    #For timeslicing 
    hours = range(1,25)

    ###########################################
    # ACCOUNT FOR PEAK SQUISHING
    ###########################################

    #Read in complited actual loads that have been cleaned for DST
    dfDemandRaw = functions.getLoadValues()

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
                regionReserveMargin = regionReserveMargin + (dfDemand.loc[year, province] / totalDemand) * PROVINCIAL_RESERVE_MARGIN[province]
            
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
    dfReserveMarginUsa = usa_data_functions.getReserveMargin()
    dfReserveMargin = dfReserveMargin.append(dfReserveMarginUsa)
    dfReserveMargin.to_csv('../src/data/ReserveMargin.csv', index=False)

    dfReserveMarginFuel = pd.DataFrame(reserveMarginTagFuel,columns=['REGION','FUEL','YEAR','VALUE'])
    dfReserveMarginFuelUsa = usa_data_functions.getReserveMarginTagFuel()
    dfReserveMarginFuel = dfReserveMarginFuel.append(dfReserveMarginFuelUsa)
    dfReserveMarginFuel.to_csv('../src/data/ReserveMarginTagFuel.csv', index=False)

    dfReserveMarginTech = pd.DataFrame(reserveMarginTagTech,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfReserveMarginTechUsa = usa_data_functions.getReserveMarginTagTechnology()
    dfReserveMarginTech = dfReserveMarginTech.append(dfReserveMarginTechUsa)
    dfReserveMarginTech.to_csv('../src/data/ReserveMarginTagTechnology.csv', index=False)

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