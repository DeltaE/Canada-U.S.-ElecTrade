import pandas as pd
import os
import numpy as np
import datetime

def main():
    # PURPOSE: Creates otoole formatted CapacityFactor.csv datafile 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary holds Provice to Region mapping 
    regions = {
        'W':['BC','AB'],
        'MW':['SAS','MAN'],
        'ME':['ONT','NB'],
        'E':['QC','NS','PEI','NL']}

    #Dictionary holds month to season Mapping 
    seasons = {
        'W':[1, 2, 3],
        'SP':[4, 5, 6],
        'S':[7, 8, 9],
        'F':[10, 11, 12]}

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Capacity Factor Calculations
    ###########################################

    #Get df for all capacity factors
    dfWind = renewableNinjaData('WN', regions, seasons, years)
    dfPV = renewableNinjaData('PV', regions, seasons, years)
    #dfHydro = capFactorHydro(regions, seasons, years)
    dfFossil = read_NREL(regions, seasons, years)

    ###########################################
    # Writing Capacity Factor to File 
    ###########################################

    #output dataframe 
    df = pd.DataFrame(columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])

    #Append technologies to output dataframe
    df = df.append(dfWind)
    df = df.append(dfPV)
    #df = df.append(dfHydro)
    df = df.append(dfFossil)

    #Print capactiyFactor dataframe to a csv 
    df.to_csv('..\\src\\data\\CapacityFactor.csv', index=False)
    
def renewableNinjaData(tech, regions, seasons, years):
    # PURPOSE: Takes a folder of CSVs created by renewable Ninja and formats a dataframe to hold all capacity factor values 
    # INPUT:   Name of the tech ('WIND' or 'PV') - CSVs in folder named (<TECH>_<PROVINCE>.csv)
    #          Regions: Disctionary showing region to province mapping
    #          Seasons: Dictionary showing season to month mapping 
    #          Years: List of years to populate values for 
    # OUTPUT:  otoole formatted dataframe holding capacity factor values for input tech type 

    #Dictionary to hold land area for averaging (thousand km2)
    landArea = {
        'BC':945,
        'AB':661,
        'SAS':651,
        'MAN':647,
        'ONT':1076,
        'QC':1542,
        'NB':73,
        'NL':405,
        'NS':55,
        'PEI':6}

    #TimeSlices to print over
    hourList = range(1,25)
    
    #Holds data to be written to a csv
    data = []

    #get formatted data for each region and append to output dataframe
    for region in regions: 
        dfProvince = pd.DataFrame(columns = ['PROVINCE','SEASON','HOUR','VALUE'])
        for province in regions[region]: 
            csvName = tech + '_' + province + '.csv'
            dfTemp = readRenewableNinjaCSV(csvName, province)
            dfTemp = monthlyAverageCF(dfTemp)
            dfTemp = seasonalAverageCF(dfTemp, seasons)
            dfProvince = dfProvince.append(dfTemp, ignore_index = True)

        #Find total land area of region for calcaulting weighted averages
        regionLandArea = 0
        for province in regions[region]:
            regionLandArea = regionLandArea + landArea[province]

        #Filter dataframe for each season and timeslice 
        for year in years:
            print (f"{region} {tech} {year}")
            for season in seasons:
                #for month in seasons[season]:
                for hour in hourList: 
                    dfFilter = dfProvince.loc[(dfProvince['SEASON'] == season) & (dfProvince['HOUR'] == hour)]
                    provinces = list(dfFilter['PROVINCE'])
                    cfList = list(dfFilter['VALUE'])

                    #Find average weighted average capacity factor
                    cf = 0
                    for i in range(len(provinces)):
                        weightingFactor = landArea[provinces[i]]/regionLandArea
                        cf = cf + cfList[i]*weightingFactor

                    #create timeslice value 
                    ts = season + str(hour)

                    #Append data to output data list 
                    data.append([region, tech, ts, year, cf])
                    #newRow = {'REGION':region,'TECHNOLOGY':tech,'TIMESLICE':ts,'YEAR':year,'VALUE':cf}
                    #df = df.append(newRow, ignore_index=True)
        
    #output dataframe 
    df = pd.DataFrame(data, columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    return df

def readRenewableNinjaCSV(csvName, province):
    # PURPOSE: Reads in raw renewable ninja file, removes everything except local time and CF value, 
    # parses the date column to seperate month, day, and hour columns
    # INPUT: Name of csv file to read in WITH csv extension (.csv)
    # OUTPUT: Dataframe with the columns: Province, Month, Day, Hour, CF Value 

    #Path to file to read
    sourceFile = '..\\dataSources\\CapacityFactor\\' + csvName

    #read in csv
    df = pd.read_csv(sourceFile, header=None, skiprows=[0,1,2,3])

    # Drop everything except columns 2,3 (Local time and capacity factor)
    # df.drop(df.columns[0],axis=1,inplace=True)
    df = df[[df.columns[1],df.columns[2]]]

    #add headers and parse to lists 
    df.columns = ['date','value']
    dateList = df['date'].tolist()
    cfList = df['value'].tolist()

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

    #List to hold all data in to be written to a dataframe
    data = []

    #loop over list and break out month, day, hour from date
    for i in range(len(dateList)):
        dateFull = dateList[i]
        date = datetime.datetime.strptime(dateFull, '%Y-%m-%d %H:%M')

        #Add 1 to the hour because renewableNinja gives hours on 0-23 scale and we want 1-24 scale
        hourAdjusted = date.hour + 1

        #Shift time values to match BC time (ie. Shift 3pm Alberta time back one hour, so all timeslices represent the asme time)
        hourAdjusted = hourAdjusted - timeZone[province]
        if hourAdjusted < 1:
            hourAdjusted = hourAdjusted + 24
        
        #Save data
        data.append([province, date.month, date.day, hourAdjusted, cfList[i]])

    #dataframe to output 
    dfOut = pd.DataFrame(data,columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])
    return dfOut

def monthlyAverageCF(dfIn):
    # PURPOSE: Reduces a yearly, hourly df so each month is represented by one day 
    # INPUT: a full year hourly dataframe giving cf values (columns = province, month, day, hour, value)
    # OUTPUT: dataframe giving the average day per month (columns = province, month, hour, value)

    #Values to filter over
    months = range(1,13)
    hours = range(1,25)

    #List to hold all data in to be written to a dataframe
    data = []

    #filter input dataframe to show all hours for one month 
    for month in months:
        for hour in hours: 
            dfTemp = dfIn.loc[(dfIn['MONTH']==month) & (dfIn['HOUR']==hour)]
            dfTemp.reset_index(drop=True, inplace=True)
            data.append([dfIn['PROVINCE'].iloc[0], month, hour, dfTemp['VALUE'].mean()])
    
    #dataframe to output 
    dfOut = pd.DataFrame(data,columns = ['PROVINCE','MONTH','HOUR','VALUE'])
    return dfOut 

def seasonalAverageCF(dfIn, seasons):
    # PURPOSE: Reduces a dataframe giving one average CF day per month, to one average CF day per season
    # INPUT: dfIn: Dataframe giving the average day per month (columns = province, month, hour, value)
    #        Seasons: Dictionary showing season to month mapping 
    # OUTPUT: Dataframe giving the average day per season (columns = province, season, hour, value)

    #Valeus to iterate over 
    hours = range(1,25)

    #List to hold all data in to be written to a dataframe
    data = []

    #filter input dataframe to show all hours for one month 
    for season in seasons:
        for hour in hours:
            cf = 0
            for month in seasons[season]: 
                dfTemp = dfIn.loc[(dfIn['MONTH'] == month) & (dfIn['HOUR']==hour)]
                dfTemp.reset_index(drop=True, inplace=True)
                cf = cf + dfTemp.loc[0,'VALUE']
            cf = cf/len(seasons[season])
            data.append([dfIn['PROVINCE'].iloc[0], season, hour, cf])
                
    #dataframe to output 
    dfOut = pd.DataFrame(data,columns = ['PROVINCE','SEASON','HOUR','VALUE'])
    return dfOut 

def capFactorHydro(regions, seasons, years):
    # PURPOSE: Calulates the capacityFactor for Hydro for Canadian regions 
    # INPUT:   Regions: Disctionary showing region to province mapping 
    #          Seasons: Dictionary showing season to month mapping 
    #          Years: List of years to populate values for 
    # OUTPUT:  otoole formatted dataframe holding hydro capacity factor values 
    
    #####################################################
    ## CAPACITIES AND GENERATION FOR 2017 HARDCODED IN ##
    ##              WILL NEED TO UPDATE                ##
    #####################################################

    # Residual Hydro Capacity (GW), Total Generation (TWh), and hydro generation (TWh) per province in 2017
    inData = {
        'BC':  [15.407,  74.483,  66.510],
        'AB':  [1.218,   81.404,   2.050],
        'SAS': [0.867,   24.739,   3.862],
        'MAN': [5.461,   37.076,  35.991],
        'ONT': [9.122,  152.745,  39.492],
        'QC':  [40.438, 214.375, 202.001],
        'NB':  [0.968,   13.404,   2.583],
        'NL':  [6.762,   39.069,  36.715],
        'NS':  [0.370,   10.034,   0.849],
        'PEI': [0.000,    0.615,   0.000]}
    # Residual Capacity: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startYear=2017&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20170101
    # Generation Source: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startMonth=01&cubeTimeFrame.startYear=2017&cubeTimeFrame.endMonth=12&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20171201
  
    #calculate capacity factor for each province 
    cf = {}
    for region in regions:
        generation = 0 #TWh
        capacity = 0 #TW
        #calcualte totals for region 
        for province in regions[region]:
            capacity = capacity + inData[province][0]
            generation = generation + inData[province][2]
        
        #save total capacity factor
        cf[region] = (generation*(1000/8760))/capacity

    #TimeSlices to print over
    hourList = range(1,25)
    
    #set up output dataframe 
    df = pd.DataFrame(columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])

    #Populate output dataframe 
    for year in years:
        print(f'Hydro {year}')
        for region in regions:
            for season in seasons:
                for hour in hourList: 

                    #create timeslice value 
                    ts = season + str(hour)

                    newRow = {'REGION':region,'TECHNOLOGY':'HYD','TIMESLICE':ts,'YEAR':year,'VALUE':cf[region]}
                    df = df.append(newRow, ignore_index=True)
    
    return df

def read_NREL(regions, seasons, years):
    # PURPOSE: reads the NREL raw excel data sheet
    # INPUT:   regions: List holding what regions to print values over
    #          Seasons: Dictionary showing season to month mapping 
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding capacity factor values 

    #global filtering options
    scenario = 'Moderate'
    crpYears = 20
    metric_case = 'Market'
    
    # Dictionary key is technology abbreviation in our model
    # Dictionay value list holds how to filter input data frame 
    # Max three list values match to columns [technology, techdetail, Alias]
    technology = {
        'CL':['Coal', 'IGCCHighCF'] ,
        'CLCCS':['Coal', 'CCS30HighCF'] ,
        'NGCC': ['NaturalGas','CCHighCF'],
        'NGCT': ['NaturalGas','CTHighCF'],
        'NUC': ['Nuclear'],
        'BIO': ['Biopower','Dedicated'],
    }

    #read in file 
    sourceFile = '..\\dataSources\\NREL_Costs.csv'
    dfRaw = pd.read_csv(sourceFile, index_col=0)

    #filter out all numbers not associated with atb 2020 study 
    dfRaw = dfRaw.loc[dfRaw['atb_year'] == 2020]

    #drop all columns not needed
    dfRaw.drop(['atb_year','core_metric_key','Default'], axis=1, inplace=True)

    #apply global filters
    dfFiltered = dfRaw.loc[
        (dfRaw['core_metric_case'] == metric_case) & 
        (dfRaw['crpyears'] == crpYears) & 
        (dfRaw['scenario'] == scenario)]

    #apply capacity factor filter
    dfCF = dfFiltered.loc[dfFiltered['core_metric_parameter'] == 'CF']
    
    #List to hold all output data
    #columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE']
    data = []

    #TimeSlices to print over
    hourList = range(1,25)

    #used for numerical indexing over columns shown in cost type for loop
    colNames = list(dfCF) 

    #Loop over regions and years 
    for region in regions:
        for year in years:

            #filter based on years
            dfYear = dfCF.loc[dfCF['core_metric_variable'] == year]

            #loop over technologies that contribute to total cost 
            for tech, techFilter in technology.items():

                #Filter to get desired technology
                dfTech = dfYear
                for i in range(len(techFilter)): 
                    dfTech = dfTech.loc[dfTech[colNames[i+3]] == techFilter[i]]

                #There should only be one line item left at this point
                if len(dfTech) > 1:
                    print(f'There are {len(dfTech)} rows in the {year} {tech} dataframe')
                    print('DATA NOT WRITTEN!')
                    exit()
                elif len(dfTech) < 1:
                    print(f'{tech} has a capacity factor of one in {year} for the {region} region')
                    cf = 1
                else:
                    #extract capaity factor
                    cf = dfTech.iloc[0]['value']

                #write data for all timeslices in the year
                for season in seasons:
                    for hour in hourList:
                        ts = season + str(hour)

                        #write data to output list
                        data.append([region, tech, ts, year, cf])
                
    df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    return df

if __name__ == "__main__":
    main()
