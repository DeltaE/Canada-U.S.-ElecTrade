import pandas as pd
import os
import numpy as np
import datetime
import functions
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted ReserveMargin, ReserveMarginTagFuel, and 
    #          ReserveMarginTagTechnology CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dict')['CAN'] # Canadian subregions
    seasons = functions.getFromYaml('seasons')
    techTags = functions.getFromYaml('techs_master')
    variableTechs = functions.getFromYaml('variable_techs')
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

    # Make list of techs to tag by removing the non-dispachable techs from techTags
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
    for subregion, provinces in canSubregions.items():
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

    for subregion, provinces in canSubregions.items():
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
    for year in years:
        reserveMargin.append([continent, year, 1])

    #reserve margin Tag Fuel = Region, Fuel, Year, Value
    reserveMarginTagFuel = []
    for i in range(len(reserveMarginRaw)):
        fuelName = 'ELC' + 'CAN' + reserveMarginRaw[i][0] + '01'
        year = reserveMarginRaw[i][1]
        rm = reserveMarginRaw[i][2]
        rm = round(rm,3)
        reserveMarginTagFuel.append([continent, fuelName, year, rm])
    
    #reserve margin Tag Technology = Region, Technology, Year, Value
    reserveMarginTagTech = []
    for subregion in canSubregions:
        for year in years:
            for tech in techTags:
                techName = 'PWR' + tech + 'CAN' + subregion + '01'
                reserveMarginTagTech.append([continent, techName, year, 1])

    #write out all files
    dfReserveMargin = pd.DataFrame(reserveMargin,columns=['REGION','YEAR','VALUE'])
    dfReserveMarginUsa = getUsaReserveMargin()
    dfReserveMargin = dfReserveMargin.append(dfReserveMarginUsa)
    dfReserveMargin.to_csv('../src/data/ReserveMargin.csv', index=False)

    dfReserveMarginFuel = pd.DataFrame(reserveMarginTagFuel,columns=['REGION','FUEL','YEAR','VALUE'])
    dfReserveMarginFuelUsa = getUsaReserveMarginTagFuel()
    dfReserveMarginFuel = dfReserveMarginFuel.append(dfReserveMarginFuelUsa)
    dfReserveMarginFuel.to_csv('../src/data/ReserveMarginTagFuel.csv', index=False)

    dfReserveMarginTech = pd.DataFrame(reserveMarginTagTech,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfReserveMarginTechUsa = getUsaReserveMarginTagTechnology()
    dfReserveMarginTech = dfReserveMarginTech.append(dfReserveMarginTechUsa)
    dfReserveMarginTech.to_csv('../src/data/ReserveMarginTagTechnology.csv', index=False)

def getUsaReserveMarginTagTechnology():
    # PURPOSE: Creates getReserveMarginTagTechnology file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    continent = functions.getFromYaml('continent')
    techMap = functions.getFromYaml('usa_tech_map')
    variableTechs = functions.getFromYaml('variable_techs')
    years = functions.getYears()

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'ReserveMarginInTagTech(r,t,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #list to hold output data
    outData=[]

    #get list of american subregions
    usaSubregions = df['REGION']
    usaSubregions = list(set(usaSubregions))

    #populate data 
    for techOld in techMap:
        for year in years:
            for subregion in usaSubregions:
                techMapped = techMap[techOld]
                tech = 'PWR' + techMapped + 'USA' + subregion + '01'
                if techMapped in variableTechs:
                    value = 0
                else:
                    value = 1
                outData.append([continent,tech,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getUsaReserveMarginTagFuel():
    # PURPOSE: Creates ReserveMarginTagFuel file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    # Due to our naming convention, we actually want to assign reserve margin value
    # to reservemargintagfuel

    ##################################################
    # Account for peak squishing 
    ##################################################

    # Region Dictionary
    usaSubregions = functions.getFromYaml('regions_dict')['USA'] # American subregions
    continent = functions.getFromYaml('continent')
    years = functions.getYears()

    # Should update this for individual provinces
    # should be 10 percent for hydro dominated provinces or 
    # 15 percent for thermal dominated regions 
    baseRM = {
        'NW':1.15,
        'CA':1.15,
        'MN':1.15,
        'SW':1.15,
        'CE':1.15,
        'TX':1.15,
        'MW':1.15,
        'AL':1.15,
        'MA':1.15,
        'SE':1.15,
        'FL':1.15,
        'NY':1.15,
        'NE':1.15
    }

    sourceFile = '../dataSources/USA_Demand.xlsx'
    dfDemand = pd.read_excel(sourceFile, sheet_name='AnnualDemand')
    dfProfile = pd.read_excel(sourceFile, sheet_name='HourlyDemand')

    #rename profile dataframe columns
    dfProfile = dfProfile.rename(columns={'CAL Demand (MWh)':'CA',
                                        #'CAR Demand (MWh)':'',
                                        'CENT Demand (MWh)':'CE',
                                        'FLA Demand (MWh)':'FL',
                                        'MIDA Demand (MWh)':'MA',
                                        'MIDW Demand (MWh)':'MW',
                                        'NE Demand (MWh)':'NE',
                                        'NW Demand (MWh)':'NW',
                                        'NY Demand (MWh)':'NY',
                                        'SE Demand (MWh)':'AL',
                                        'SW Demand (MWh)':'SW',
                                        'TEN Demand (MWh)':'SE',
                                        'TEX Demand (MWh)':'TX'})

    #Fill in overlapping regions (these will have the same reserve margin)
    dfProfile = dfProfile.drop(columns=['CAR Demand (MWh)'])
    dfProfile['MN'] = dfProfile['NW']

    #Get total annual demand 
    annualDemand = dict()
    for subregion, provinces in usaSubregions.items():
        regionalDemand = 0
        for province in provinces:
            regionalDemand = regionalDemand + dfDemand.loc[dfDemand['Abr.']==province]['PJ'].sum()
        if province == 'MD': #DC not by default included in demand 
            regionalDemand = regionalDemand + dfDemand.loc[dfDemand['Abr.']=='DC']['PJ'].sum()
        annualDemand[subregion] = regionalDemand

    #Normalize the load profiles 
    maxDemandDict = dict()
    for subregion in usaSubregions:
        maxDemand = dfProfile[subregion].max()
        totalDemand = dfProfile[subregion].sum()
        maxDemandDict[subregion] = maxDemand / totalDemand

    # Actual Peak Demand
    actualPeak = dict()
    for subregion in usaSubregions:
        actualPeak[subregion] = maxDemandDict[subregion] * annualDemand[subregion]

    #Modeled peak Demand
    dfModeledProfile = pd.read_excel('../dataSources/USA_Data.xlsx','SpecifiedDemandProfile(r,f,l,y)')

    #remove everything except 2019
    dfModeledProfile = dfModeledProfile.loc[(dfModeledProfile['YEAR'] > 2018) &
                                            (dfModeledProfile['YEAR']< 2020)]
    dfModeledProfile.reset_index()

    #get max modelled peak 
    modelledPeak = dict()
    for subregion in usaSubregions:
        maxProfile = dfModeledProfile.loc[(dfModeledProfile['REGION'] == subregion)]['DEMAND'].max()
        modelledPeak[subregion]=maxProfile * annualDemand[subregion] * (96/8960)

    #calculate adjusted reserve margin 
    reserveMargin = dict()
    for subregion in usaSubregions:
        reserveMargin[subregion] = baseRM[subregion] + (actualPeak[subregion] - modelledPeak[subregion]) / actualPeak[subregion]

    #list to hold output data
    outData=[]

    #populate data 
    for year in years:
        for subregion in usaSubregions:
            fuel = 'ELC' + 'USA' + subregion + '01'
            value = reserveMargin[subregion]
            outData.append([continent,fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','FUEL','YEAR','VALUE'])
    return dfOut

def getUsaReserveMargin():
    # PURPOSE: Creates ReserveMargin file
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    continent = functions.getFromYaml('continent')
    years = functions.getYears()

    #this one is easier to manually do...
    outData = []

    for year in years:
        outData.append([continent,year,1])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()  