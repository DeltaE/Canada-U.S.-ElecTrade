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
    'SK':2,
    'MB':2,
    'ON':3,
    'QC':3,
    'NB':4,
    'NL':4,
    'NS':4,
    'PE':4}

#####################################
# COMMON FUNCTIONS
#####################################
def getFromYaml(name):
    # PURPOSE: Returns a value from the configured config.yaml file,
    # which is a modifiable settings file that contains constants
    # INPUT: name = the name of the value being retrieved
    # OUTPUT: parsedYaml = the ready-to-use yaml file

    originalYaml = open("../scripts/config.yaml")
    parsedYaml = yaml.load(originalYaml, Loader=yaml.FullLoader).get(name)
    return parsedYaml

def getYears():
    # PURPOSE: Retrieves a list of years used
    # in the model from the config.yaml file
    # INPUT:   None
    # OUTPUT:  years = list of applicable years in the model

    startYear = getFromYaml('start_year')
    endYear = getFromYaml('end_year')

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

def getPWRtechs(region, techs):
    # PURPOSE: Creates all the PWR naming technologies
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the PWR technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for subregion in region[1].keys():

        print(region, subregion)

        for tech in techs:
            techName = 'PWR' + tech + region[0] + subregion + '01'
            outList.append(techName)
    
    # Return list of pwr Technologes
    return outList

def getPWRTRNtechs(region):
    # PURPOSE: Creates all the PWRTRN naming technologies
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    # OUTPUT:  outList =  List of all the PWR technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        techName = 'PWR' + 'TRN' + region[0] + subregion
        outList.append(techName)
    
    # Return list of pwr Technologes
    return outList

def getMINtechs(region, techs):
    # PURPOSE: Creates all the MIN naming technologies
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the MIN technologies

    # list to hold technologies
    outList = []

    # Loop to create all regionalized technology names
    for tech in techs:
        techName = 'MIN' + tech + region[0]
        outList.append(techName)

    # Return list of min Technologes
    return outList

def getRNWtechs(region, techs):
    # PURPOSE: Creates all the RNW naming technologies
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the RNW technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        for tech in techs:
            techName = 'RNW' + tech + region[0] + subregion
            outList.append(techName)
    
    # Return list of rnw Technologes
    return outList

def getTRNtechs(csvPath):
    # PURPOSE: Creates all the TRN naming technologies
    # INPUT:   csvPath = Transmission csv path
    # OUTPUT:  outList =  List of all the TRN technologies

    df = pd.read_csv(csvPath)
    outList = df['TECHNOLOGY'].tolist()
    outList = list(set(outList)) # remove duplicates

    return outList

def getRNWfuels(region, techs):
    # PURPOSE: Creates fuels names for Renewable technologies
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the RNW technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        for tech in techs:
            fuelName = tech + region[0] + subregion
            outList.append(fuelName)
    
    # Return list of rnw fuels
    return outList

def getMINfuels(region, techs):
    # PURPOSE: Creates Fuel names for Mined Fuels
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the MIN Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names based on region
    for tech in techs:
        fuelName = tech + region[0]
        outList.append(fuelName)

    # Return list of min TFuels
    return outList

def getELCfuels(region):
    # PURPOSE: Creates Fuel electricity use fuel names
    # INPUT:   region =  Tuple holding country as the key and subregion as the values in a dictionary
    #                     (CAN, {WS:[...], MW:[]...},)
    # OUTPUT:  outList =  List of all the ELC Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        elcOne = 'ELC' + region[0] + subregion + '01'
        elcTwo = 'ELC' + region[0] + subregion + '02'
        outList.extend([elcOne, elcTwo])
    
    # Return list of electricty fuels
    return outList

def createFuelDataframe(subregions, rnwFuels, mineFuels):
    # PURPOSE: Appends all fuel name lists together and writes them to a CSV
    # INPUT:   subregions = Dictionary holding Country and regions ({CAN:{WS:[...], ...}, USA:[NY:[...],...]})
    #          rnwFuels = List of the fuels to print over for getRNWfuels
    #          mineFuels = List of the fuels to print over for getMINfuels
    # OUTPUT:  dfOut = fuel set dataframe

    outputFuels = []
    for region in subregions.items():
        # Renewable fuels
        rnwFuelList = getRNWfuels(region, rnwFuels)

        # Mining fuels
        minFuelList = getMINfuels(region, mineFuels)

        #ELC fuels
        elcFuelList = getELCfuels(region)

        #Hydrogen Fuels
        #hy2FuelList = getHY2fuels(countries)

        #Append lists together
        outputFuels += rnwFuelList
        outputFuels += minFuelList
        outputFuels += elcFuelList
        #outputFuels.append(hy2FuelList)
    
    # Loop to create all technology names for international import/export
    for fuel in mineFuels:
        fuelName = fuel + 'INT'
        outputFuels.append(fuelName)
    for fuel in mineFuels:
        outputFuels.append(fuel)

    dfOut = pd.DataFrame(outputFuels, columns=['VALUE'])
    
    return dfOut

def createTechDataframe(subregions, techsMaster, mineFuels, rnwFuels, trnTechsCsvPath):
    # PURPOSE: Appends technology and fuel name lists together and returns them as a CSV dataframe
    # INPUT:   subregions = Dictionary holding Country and regions ({CAN:{WS:[...], ...} USA:[NY:[...],...]})
    #          techsMaster = List of the technologies to print over for getPWRtechs
    #          mineFuels = List of the fuels to print over for getMINfuels
    #          rnwFuels = List of the fuels to print over for getRNWfuels
    #          trnTechsCsvPath = Transmission csv information locations
    # OUTPUT:  dfOut = tech set dataframe
    # get power generator technology list 
    outputTechs = []
    for region in subregions.items():

        pwrList = getPWRtechs(region, techsMaster)

        # get grid distribution technology list (PWRTRN<Reg><SubReg>)
        pwrTrnList = getPWRTRNtechs(region)

        # get Mining techs list
        minList = getMINtechs(region, mineFuels)

        # get Renewables fuels list 
        rnwList = getRNWtechs(region, rnwFuels)

        #Append lists together
        outputTechs += pwrList
        outputTechs += pwrTrnList
        outputTechs += minList
        outputTechs += rnwList 

    # get trade technology list 
    trnList = getTRNtechs(trnTechsCsvPath)
    outputTechs += trnList
    
    #Generate international trade 
    for tech in mineFuels:
        techName = 'MIN' + tech + 'INT'
        outputTechs.append(techName)

    dfOut = pd.DataFrame(outputTechs, columns=['VALUE'])

    return dfOut

def createTechList(techsMaster, rnwTechs, mineTechs, stoTechs):
    # PURPOSE: Merges several tech lists into 'data' so that they can be printed over
    # INPUT:   techsMaster = List of the technologies to print over for power techs
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

def getUsaCapacityOrAvailabilityFactor(isCapacity):
    # PURPOSE: Creates CapacityFactor or AvailabilityFactor file from USA data
    # INPUT:   isCapacity = Boolean indicating Capacity Factor should be returned
    # when True, and Availabiltiy Factor otherwise
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #capacity factor only specified for 2015 and 2016
    #df = df.loc[df['YEAR'] == 2016]
    #df.reset_index()

    techMap = getFromYaml('usa_tech_map')
    continent = getFromYaml('continent')
    years = getYears() # years to print capacity factor over

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'CapacityFactor(r,t,l,y)')

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)
    df = dfFiltered
    df.reset_index()

    #holds output data
    outDataCF = [] # Capacity Factor
    outDataAF = [] # Availability Factor

    #map data
    for year in years:
        for i in range(len(df)):
            techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
            ts = df['TIMESLICE'].iloc[i]
            value = df['CAPACITYFACTOR'].iloc[i]
            value = round(value, 3)
            if techMapped == 'HYD':
                outDataAF.append([continent,tech,ts,year,value])
            else:
                outDataCF.append([continent,tech,ts,year,value])

    #create and return dataframe for CAPACITY FACTOR
    dfOutCF = pd.DataFrame(outDataCF, columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])

    if isCapacity: # Return Capacity Factor
        return dfOutCF
    else: # Return Availability Factor
        dfAf = pd.DataFrame(outDataAF, columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
        afTechs = dfAf['TECHNOLOGY'].to_list()
        afTechs = list(set(afTechs))

        outDataAF = [] 
        for tech in afTechs:
            dfTemp = dfAf.loc[dfAf['TECHNOLOGY'] == tech]
            for year in years:
                dfYear = dfTemp.loc[dfTemp['YEAR'] == year]
                af = dfYear['VALUE'].mean()
                af = round(af, 3)
                outDataAF.append([continent,tech,year,af])
        
        # return dataframe for CAPACITY FACTOR
        dfOutAF = pd.DataFrame(outDataAF, columns = ['REGION','TECHNOLOGY','YEAR','VALUE'])
        return dfOutAF