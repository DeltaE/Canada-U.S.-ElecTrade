import pandas as pd
import datetime
import functions
from collections import defaultdict

def main():
    # PURPOSE: Creates an otoole formatted CSV holding capacity for all technologies. If Hydro Capacity Factors are used, be sure to remove hydro availabilty factor  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    seasons = functions.openYaml().get('seasons')
    regions = functions.openYaml().get('regions')
    subregions = functions.openYaml().get('subregions_dictionary')
    years = functions.getYears()

    ###########################################
    # Capacity Factor Calculations
    ###########################################

    #Get df for all capacity factors
    dfWind = renewableNinjaData('WND', regions, subregions, seasons, years)
    dfPV = renewableNinjaData('SPV', regions, subregions, seasons, years)
    #dfHydro = capFactorHydro(subregions, seasons, years)
    dfFossil = read_NREL(regions, subregions, seasons, years)

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
    dfUsa = functions.getUsaCapacityOrAvailabilityFactor(True)
    df = df.append(dfUsa)
    df.to_csv('../src/data/CapacityFactor.csv', index=False)
    
def renewableNinjaData(tech, regions, subregions, seasons, years):
    # PURPOSE: Takes a folder of CSVs created by renewable Ninja and formats a dataframe to hold all capacity factor values 
    # INPUT:   Name of the tech ('WIND' or 'PV') - CSVs in folder named (<TECH>_<PROVINCE>.csv)
    #          Regions: List holding regions to print over
    #          Subregions: Dictionary showing region to province mapping
    #          Seasons: Dictionary showing season to month mapping 
    #          Years: List of years to populate values for 
    # OUTPUT:  otoole formatted dataframe holding capacity factor values for input tech type 

    #Dictionary to hold land area for averaging (thousand km2)
    PROVINCIAL_LAND_AREAS = {
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
        for subregion in subregions: 
            dfProvince = pd.DataFrame(columns = ['PROVINCE','SEASON','HOUR','VALUE'])
            for province in subregions[subregion]: 
                csvName = tech + '_' + province + '.csv'
                dfTemp = readRenewableNinjaCSV(csvName, province)
                dfTemp = monthlyAverageCF(dfTemp)
                dfTemp = seasonalAverageCF(dfTemp, seasons)
                dfProvince = dfProvince.append(dfTemp, ignore_index = True)

            #Find total land area of region for calcaulting weighted averages
            regionLandArea = 0
            for province in subregions[subregion]:
                regionLandArea = regionLandArea + PROVINCIAL_LAND_AREAS[province]

            #Filter dataframe for each season and timeslice 
            for year in years:
                print (f"{subregion} {tech} {year}")
                for season in seasons:
                    #for month in seasons[season]:
                    for hour in hourList: 
                        dfFilter = dfProvince.loc[(dfProvince['SEASON'] == season) & (dfProvince['HOUR'] == hour)]
                        provinces = list(dfFilter['PROVINCE'])
                        cfList = list(dfFilter['VALUE'])

                        #Find average weighted average capacity factor
                        cf = 0
                        for i in range(len(provinces)):
                            weightingFactor = PROVINCIAL_LAND_AREAS[provinces[i]]/regionLandArea
                            cf = cf + cfList[i]*weightingFactor
                        
                        #round cf
                        cf = round(cf,3)

                        #create timeslice value 
                        ts = season + str(hour)

                        #create tech name
                        techName = 'PWR' + tech + 'CAN' + subregion + '01'

                        #Append data to output data list 
                        data.append([region, techName, ts, year, cf])
        
    #output dataframe 
    df = pd.DataFrame(data, columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    return df

def readRenewableNinjaCSV(csvName, province):
    # PURPOSE: Reads in raw renewable ninja file, removes everything except local time and CF value, 
    # parses the date column to seperate month, day, and hour columns
    # INPUT: Name of csv file to read in WITH csv extension (.csv)
    # OUTPUT: Dataframe with the columns: Province, Month, Day, Hour, CF Value 

    #Path to file to read
    sourceFile = '../dataSources/CapacityFactor/' + csvName

    #read in csv
    df = pd.read_csv(sourceFile, header=None, skiprows=[0,1,2,3])

    # Drop everything except columns 2,3 (Local time and capacity factor)
    # df.drop(df.columns[0],axis=1,inplace=True)
    df = df[[df.columns[1],df.columns[2]]]

    #add headers and parse to lists 
    df.columns = ['date','value']
    dateList = df['date'].tolist()
    cfList = df['value'].tolist()

    #List to hold all data in to be written to a dataframe
    data = []

    #loop over list and break out month, day, hour from date
    for i in range(len(dateList)):
        dateFull = dateList[i]
        date = datetime.datetime.strptime(dateFull, '%Y-%m-%d %H:%M')

        #Add 1 to the hour because renewableNinja gives hours on 0-23 scale and we want 1-24 scale
        hourAdjusted = date.hour + 1

        #Shift time values to match BC time (ie. Shift 3pm Alberta time back one hour, so all timeslices represent the asme time)
        hourAdjusted = hourAdjusted - functions.PROVINCIAL_TIME_ZONES[province]
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

def read_NREL(regions, subregions, seasons, years):
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
        'COA':['Coal', 'IGCCHighCF'] ,
        'COC':['Coal', 'CCS30HighCF'] ,
        'CCG': ['NaturalGas','CCHighCF'],
        'CTG': ['NaturalGas','CTHighCF'],
        'URN': ['Nuclear'],
        'BIO': ['Biopower','Dedicated'],
    }

    #read in file 
    sourceFile = '../dataSources/NREL_Costs.csv'
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
        for subregion in subregions:
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
                        print(f'{tech} has a capacity factor of one in {year} for the {subregion} region')
                        cf = 1
                    else:
                        #extract capaity factor
                        cf = dfTech.iloc[0]['value']
                        cf = round(cf,3)

                    #write data for all timeslices in the year
                    for season in seasons:
                        for hour in hourList:

                            #timeslice name 
                            ts = season + str(hour)

                            #tech name
                            techName = 'PWR' + tech + 'CAN' + subregion + '01'

                            #write data to output list
                            data.append([region, techName, ts, year, cf])
                
    df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    return df

if __name__ == "__main__":
    main()
