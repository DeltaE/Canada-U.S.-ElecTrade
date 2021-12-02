#####################################
## This file is for functions and constants common between multiple files
#####################################

import datetime
import pandas as pd
from collections import defaultdict
import yaml

#####################################
# NON-CONFIGURABLE CONSTANTS
#####################################

# Province to Time Zone Mapping
PROVINCIAL_TIME_ZONES = {
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

#####################################
# COMMON FUNCTIONS
#####################################
def openYaml():
    # PURPOSE: Returns the configured config.yaml file, which is a modifiable settings file that contains constants
    # INPUT: None
    # OUTPUT: parsedYaml = the ready-to-use yaml file

    originalYaml = open("../scripts/config.yaml")
    parsedYaml = yaml.load(originalYaml, Loader=yaml.FullLoader)
    return parsedYaml

def getYears():
    # PURPOSE: Retrieves a list of years used
    # in the model from the config.yaml file
    # INPUT:   None
    # OUTPUT:  years = list of applicable years in the model
    startYear = openYaml().get('start_year')
    endYear = openYaml().get('end_year')
    return range(startYear, endYear + 1)

def getLoadValues():
    # PURPOSE: Takes hourly load value excel sheet and converts it into a master df
    # INPUT: None
    # OUTPUT: Dataframe with the columns: Province, Month, Day, Hour, Load Value 
    #Dictionary to hold timezone shifting values 

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
            hourAdjusted = int(hourList[i]) - PROVINCIAL_TIME_ZONES[province]
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

def getPWRtechs(regions, techs):
    # PURPOSE: Creates all the PWR naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the PWR technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for tech in techs:
                techName = 'PWR' + tech + region + subregion + '01'
                outList.append(techName)
    
    # Return list of pwr Technologes
    return outList

def getPWRTRNtechs(regions):
    # PURPOSE: Creates all the PWRTRN naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the PWR technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
                techName = 'PWR' + 'TRN' + region + subregion
                outList.append(techName)
    
    # Return list of pwr Technologes
    return outList

def getMINtechs(regions, techs, generateInternational):
    # PURPOSE: Creates all the MIN naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    #          generateInternational = True/False for whether function should
    #                                  create all international mining techs
    # OUTPUT:  outList =  List of all the MIN technologies

    # list to hold technologies
    outList = []

    # Loop to create all regionalized technology names
    for region in regions:
        for tech in techs:
            techName = 'MIN' + tech + region
            outList.append(techName)
    
    # DONE ONLY IN THE CANADA SCRIPTS
    # Loop to create all international mining techs
    if generateInternational:
        for tech in techs:
            techName = 'MIN' + tech + 'INT'
            outList.append(techName)

    # Return list of min Technologes
    return outList

def getRNWtechs(regions, techs):
    # PURPOSE: Creates all the RNW naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the RNW technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for tech in techs:
                techName = 'RNW' + tech + region + subregion
                outList.append(techName)
    
    # Return list of rnw Technologes
    return outList

def getTRNtechs(csvPath):
    # PURPOSE: Creates all the TRN naming technologies
    # INPUT:   csvPath = The location of the datafile, as a path
    # OUTPUT:  outList =  List of all the TRN technologies

    # list to hold technologies
    outList = []

    #Read in the trade csv datafile 
    df = pd.read_csv(csvPath)
    outList = df['TECHNOLOGY'].tolist()
    outList = list(set(outList)) # remove duplicates
    
    # Return list of rnw Technologes
    return outList

def getRNWfuels(regions, techs):
    # PURPOSE: Creates fuels names for Renewable technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the RNW technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for tech in techs:
                fuelName = tech + region + subregion
                outList.append(fuelName)
    
    # Return list of rnw fuels
    return outList

def getMINfuels(regions, techs, generateInternational):
    # PURPOSE: Creates Fuel names for Min technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    #          generateInternational = True/False for whether function needs to create all
    #                                  technology names for international import/export
    # OUTPUT:  outList =  List of all the MIN Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names based on region
    for region in regions:
        for tech in techs:
            fuelName = tech + region
            outList.append(fuelName)
    
    # Created once in Canada scripts
    # Loop to create all technology names for international import/export
    if generateInternational:
        for tech in techs:
            fuelName = tech + 'INT'
            outList.append(fuelName)
        for tech in techs:
            outList.append(tech)

    # Return list of min TFuels
    return outList

def getELCfuels(regions):
    # PURPOSE: Creates Fuel electricity use fuel names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the ELC Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            elcOne = 'ELC' + region + subregion + '01'
            elcTwo = 'ELC' + region + subregion + '02'
            outList.extend([elcOne, elcTwo])
    
    # Return list of electricty fuels
    return outList

def createFuelSet(countries, rnwTechs, mineTechs, generateInternational):
    # PURPOSE: Appends all fuel name lists together and writes them to a CSV
    # INPUT:   countries = Dictionary holding countries as the key and subregion as the values in a list
    #          rnwTechs = List of the technologies to print over for getRNWfuels
    #          mineTechs = List of the technologies to print over for getMINfuels
    #          generateInternational = True/False for whether getMINfuels function needs to create all
    #                                  technology names for international import/export
    # OUTPUT:  dfOut = CSV datafile

    # Renewable fuels
    rnwFuelList = getRNWfuels(countries, rnwTechs)

    # Mining fuels
    minFuelList = getMINfuels(countries, mineTechs, generateInternational)

    #ELC fuels
    elcFuelList = getELCfuels(countries)

    #Hydrogen Fuels
    #hy2FuelList = getHY2fuels(countries)

    #Append lists together and write to a csv
    #outputFuels = rnwFuelList + minFuelList + elcFuelList + hy2FuelList
    outputFuels = rnwFuelList + minFuelList + elcFuelList
    dfOut = pd.DataFrame(outputFuels, columns=['VALUE'])
    return dfOut

def createTechnologySet(countries, techsMaster, mineTechs, rnwTechs, trnTechsCsvPath, generateInternational):
    # PURPOSE: Appends all technology name lists together and returns them as a CSV datafile
    # INPUT:   countries = Dictionary holding countries as the key
    #                      and subregion as the values in a list
    #          techsMaster = List of the technologies to print over for getPWRtechs
    #          mineTechs = List of the technologies to print over for getMINtechs
    #          rnwTechs = List of the technologies to print over for getRNWtechs
    #          trnTechsCsvPath = Trade csv datafile location
    #          generateInternational = True/False for whether function should
    #                                  create all international mining techs
    # OUTPUT:  outputTechs = All technology lists appended together
    #          dfOut = CSV datafile
    # get power generator technology list 
    pwrList = getPWRtechs(countries, techsMaster)

    # get grid distribution technology list (PWRTRN<Reg><SubReg>)
    pwrTrnList = getPWRTRNtechs(countries)

    # get Mining technology list
    minList = getMINtechs(countries, mineTechs, generateInternational)

    # get Renewables technology list 
    rnwList = getRNWtechs(countries, rnwTechs)

    # get trade technology list 
    trnList = getTRNtechs(trnTechsCsvPath)

    #Append lists together and write to a csv
    outputTechs = pwrList + pwrTrnList + minList + rnwList + trnList
    dfOut = pd.DataFrame(outputTechs, columns=['VALUE'])

    return outputTechs, dfOut

def createTechLists(techsMaster, rnwTechs, mineTechs, stoTechs):
    # PURPOSE: Merges several tech lists into 'data' so that they can be printed over
    # INPUT:   countries = Dictionary holding countries as the key and subregion as the values in a list
    #          techsMaster = List of the technologies to print over for power techs
    #          rnwTechs = List of the technologies to print over for renewable techs
    #          mineTechs = List of the technologies to print over for mining techs
    #          stoTechs = List of the technologies to print over for storage techs
    # OUTPUT:  data = Merged tech lists
    # get power generator technology list 
    data = []

    for i in range(len(techsMaster)):
        data.append(['PWR',techsMaster[i]])

    for i in range(len(rnwTechs)):
        data.append(['RNW',rnwTechs[i]])

    for i in range(len(mineTechs)):
        data.append(['MIN',mineTechs[i]])

    for i in range(len(stoTechs)):
        data.append(['STO',stoTechs[i]])
    
    return data

def initializeCanadaUsaModelParameters(topLevelRegion):
    # PURPOSE: Initializes necessary parameters for config.py and UsaData.py, which create
    # Tech and Fuel sets for Canada and the US, respectively
    # INPUT:   topLevelRegion = String indicating region: 'CAN' or 'USA'
    # OUTPUT:  years = List from 2019 to 2051
    #          regions = List for regions
    #          emissions = List for CO2 emissions
    #          techsMaster = List for power technologies
    #          rnwTechs = List for renewable technologies
    #          mineTechs = List for mining technologies
    #          stoTechs = List for storage technologies
    #          countries = Dictionary for holding countries as the key and subregion as the values in a list
    # get power generator technology list 

    regions = openYaml().get('regions')
    emissions = openYaml().get('emissions')
    techsMaster = openYaml().get('techs_master')
    rnwTechs = openYaml().get('rnw_techs')
    mineTechs = openYaml().get('mine_techs')
    stoTechs = openYaml().get('sto_techs')
    years = getYears()

    #Countries and subregions in the model
    countries = {
        topLevelRegion:[]
        }

    #Read in subregions. This step is needed cause other scripts use the 
    #provincial breakdown by subregion in the excel file 
    sourceFile = '../dataSources/Regionalization.xlsx'
    dfCountry = pd.read_excel(sourceFile, sheet_name=topLevelRegion)
    regionList = dfCountry['REGION'].tolist()
    regionList = list(set(regionList)) # remove duplicates
    countries[topLevelRegion] = regionList # save to dictionary
    
    return years, regions, emissions, techsMaster, rnwTechs, mineTechs, stoTechs, countries