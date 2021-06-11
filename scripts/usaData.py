import pandas as pd
import os

def main():
    # PURPOSE: Appends the USA data onto the bottom of Canada data
    # INPUT: none
    # OUTPUT: none


    ####################################
    ## MODEL PARAMETERS
    ####################################

    # Model Name 
    model = ['Canada_USA']

    # Regions in the model
    regions = ['NAmerica']

    # Years to loop over 
    years = list(range(2019,2051,1))

    # Emission Types
    emissions = ['CO2']

    # Storages
    storages = [] 

    # PWR Technologies
    techsMaster = [
        'BIO', # Biomass
        'CCG', # Gas Combind Cycle 
        'CTG', # Gas Combustion Turbine
        'COA', # Coal
        'COC', # Coal CCS
        'HYD', # Hydro 
        'SPV', # Solar
        'URN', # Nuclear
        'WND', # Wind
    ]

    #RWN Technologies
    rnwTechs = [
        'HYD', # Hydro 
        'SPV', # Solar
        'WND', # Wind
        'BIO', # Biomass
    ]

    #MIN TEchnologies
    mineTechs = [
        'COA', # Coal
        'GAS', # Gas
        'URN', # Nuclear
    ]

    #STO Technologies
    stoTechs = [
    ]

    #Countries and subregions in the model
    countries = {
        'USA':[] #Canada
        }

    #Read in subregions. This step is needed cause other scripts use the 
    #provincial breakdown by subregion in the excel file 
    sourceFile = '../dataSources/Regionalization.xlsx'
    for country in countries:
        dfCountry = pd.read_excel(sourceFile, sheet_name=country)
        regionList = dfCountry['REGION'].tolist()
        regionList = list(set(regionList)) # remove duplicates
        countries[country] = regionList # save to dictionary

    #######################################
    ## CREATE TECH LISTS FOR OTHER SCRIPTS
    #######################################
    
    data = []

    for i in range(len(techsMaster)):
        data.append(['PWR',techsMaster[i]])

    for i in range(len(rnwTechs)):
        data.append(['RNW',rnwTechs[i]])

    for i in range(len(mineTechs)):
        data.append(['MIN',mineTechs[i]])

    for i in range(len(stoTechs)):
        data.append(['STO',stoTechs[i]])

    ####################################
    ## CREATE STANDARD SETS
    ####################################

    #Regions set
    #dfOut = pd.DataFrame(regions, columns=['VALUE'])
    #dfOut.to_csv('../src/data/USA/REGION.csv', index=False)

    ####################################
    ## CREATE TECHNOLOGY SET
    ####################################

    # get power generator technology list 
    pwrList = getPWRtechs(countries, techsMaster)

    # get grid distribution technology list (PWRTRN<Reg><SubReg>)
    pwrTrnList = getPWRTRNtechs(countries)

    # get Mining technology list
    minList = getMINtechs(countries, mineTechs)

    # get Renewables technology list 
    rnwList = getRNWtechs(countries, rnwTechs)

    # get trade technology list 
    trnList = getTRNtechs()

    #Append lists together and write to a csv
    outputTechs = pwrList + pwrTrnList + minList + rnwList + trnList
    dfOut = pd.DataFrame(outputTechs, columns=['VALUE'])
    dfOut.to_csv('../src/data/USA/TECHNOLOGY.csv', index=False)

    ####################################
    ## CREATE FUEL SET
    ####################################

    # Renewable fules
    rnwFuelList = getRNWfuels(countries, rnwTechs)

    # Mining fuels
    minFuelList = getMINfuels(countries, mineTechs)

    #ELC Fules
    elcFuelList = getELCfuels(countries)

    #Append lists together and write to a csv
    outputFuels = rnwFuelList + minFuelList + elcFuelList
    dfOut = pd.DataFrame(outputFuels, columns=['VALUE'])
    dfOut.to_csv('../src/data/USA/FUEL.csv', index=False)

    ####################################
    ## READ IN MAIN EXCEL SHEET
    ####################################

    #Tech mapping USA Name -> Our Name
    techMap = {
        'BIOPP':'BIO', # Biomass
        'NGCC':'CCG', # Gas Combind Cycle 
        'NGCT':'CTG', # Gas Combustion Turbine
        'COALPP':'COA', # Coal
        'COALCCS':'COC', # Coal CCS
        'HYDROPP':'HYD', # Hydro 
        'PV':'SPV', # Solar
        'NUC':'URN', # Nuclear
        'WINDPP':'WND', # Wind
    }

    #Tech mapping USA Name -> Our Name
    inputFuelMap = {
        'BIO':'BIO', # Biomass
        'CCG':'GAS', # Gas Combind Cycle 
        'CTG':'GAS', # Gas Combustion Turbine
        'COA':'COA', # Coal
        'COC':'COA', # Coal CCS
        'HYD':'HYD', # Hydro 
        'SPV':'SPV', # Solar
        'URN':'URN', # Nuclear
        'WND':'WND', # Wind
    }

    #dictionary holding excel sheet name to parameter names
    excelToParameter = {
    'SpecifiedAnnualDemand(r,f,y)':'SpecifiedAnnualDemand',
    'SpecifiedDemandProfile(r,f,l,y)':'SpecifiedDemandProfile',
    'CapacityToActivityUnit(r,t)':'CapacityToActivityUnit',
    'CapacityFactor(r,t,l,y)':'CapacityFactor',
    'OperationalLife(r,t)':'OperationalLife',
    'ResidualCapacity(r,t,y)':'ResidualCapacity',
    'InputActivityRatio(r,t,f,m,y)':'InputActivityRatio',
    'OutputActivityRatio(r,t,f,m,y)':'OutputActivityRatio',
    'CapitalCost(r,t,y)':'CapitalCost',
    'VariableCost(r,t,m,y)':'VariableCost',
    'FixedCost(r,t,y)':'FixedCost',
    'TotalAnnualMaxCapacity(r,t,y)':'TotalAnnualMaxCapacity',
    'ReserveMarginInTagTech(r,t,y)':'ReserveMarginTagTechnology',
    'ReserveMarginInTagFuel(r,f,y)':'ReserveMarginTagFuel',
    'ReserveMargin(r,y)':'ReserveMargin',
    'RETagTechnology(r,t,y)':'RETagTechnology',
    'EmisionActivityRatio(r,t,e,m,y)':'EmissionActivityRatio',
    }

    # Read in each sheet and save it as a dataframe
    for sheet, param in excelToParameter.items():
        df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = sheet)

        if param == 'SpecifiedAnnualDemand':
            dfOut = getSpecifiedAnnualDemand(techMap, df)
        elif param == 'SpecifiedDemandProfile':
            dfOut = getSpecifiedDemandProfile(techMap, df)
        elif param == 'CapacityToActivityUnit':
            dfOut = getCapToActivityUnit(outputTechs)
        elif param == 'CapacityFactor':
            dfOut = getCapacityFactor(techMap, df)
        elif param == 'OperationalLife':
            dfOut = getOperationalLife(techMap, df)
        elif param == 'ResidualCapacity':
            dfOut = getResidualCapacity(techMap, df)
        elif param == 'InputActivityRatio':
            dfOut = getInputActivityRatio(techMap, inputFuelMap, countries, df)
        elif param == 'OutputActivityRatio':
            dfOut = getOutputActivityRatio(techMap, countries)
        elif param == 'CapitalCost':
            dfOut = getCapitalCost(techMap, df)
        elif param == 'VariableCost':
            dfOut = getVariableCost(techMap, inputFuelMap, df)
        elif param == 'FixedCost':
            dfOut = getFixedCost(techMap, df)
        elif param == 'TotalAnnualMaxCapacity':
            # Something is wrong with these values...
            # SE Residual Capacity is greater then SE Total Annual Max Capacity 
            #dfOut = getTotalAnnualMaxCapacity(techMap, df)
            dfOut = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
        elif param == 'ReserveMarginTagTechnology':
            dfOut = getReserveMarginTagTechnology(techMap, df)
        elif param == 'ReserveMarginTagFuel':
            dfOut = getReserveMarginTagFuel(techMap, df)
        elif param == 'ReserveMargin':
            dfOut = getReserveMargin()
        elif param == 'RETagTechnology':
            dfOut = getRETagTechnology(countries)
        elif param == 'EmissionActivityRatio':
            dfOut = getEmisionActivityRatio(techMap, inputFuelMap, df)

        print(f'Finished USA {param}')
        dfOut.to_csv('../src/data/USA/' + param + '.csv', index=False)

####################################
## EXTRA FUNCTIONS
####################################
 
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

def getMINtechs(regions, techs):
    # PURPOSE: Creates all the MIN naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the MIN technologies

    # list to hold technologies
    outList = []

    # Loop to create all regionalized technology names
    for region in regions:
        for tech in techs:
            techName = 'MIN' + tech + region
            outList.append(techName)
    
    # DONE IN THE CANADA SCRIPTS
    # Loop to create all international mining techs
    #for tech in techs:
    #    techName = 'MIN' + tech + 'INT'
    #    outList.append(techName)

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

def getTRNtechs():
    # PURPOSE: Creates all the TRN naming technologies
    # INPUT:   None
    # OUTPUT:  outList =  List of all the TRN technologies

    # list to hold technologies
    outList = []

    #Read in the trade csv datafile 
    df = pd.read_csv('../dataSources/USA_Trade.csv')
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

def getMINfuels(regions, techs):
    # PURPOSE: Creates Fuel names for Min technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the MIN Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names based on region
    for region in regions:
        for tech in techs:
            fuelName = tech + region
            outList.append(fuelName)
    
    #THESE ARE ALREADY CREATED IN THE CANADA SCRIPTS
    # Loop to create all technology names for international import/export
    #for tech in techs:
    #    fuelName = tech + 'INT'
    #    outList.append(fuelName)
    #for tech in techs:
    #    outList.append(tech)

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

def getSpecifiedAnnualDemand(techMap, df):
    # PURPOSE: Creates specifiedAnnualDemand file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        outData.append([region,fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    return dfOut
    
def getSpecifiedDemandProfile(techMap, df):
    # PURPOSE: Creates specifiedDeamandProfile file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        ts = df['TIMESLICE'].iloc[i]
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        outData.append([region,fuel,ts,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    return dfOut

def getCapToActivityUnit(techs):
    # PURPOSE: Creates capacityToActivity file from USA data
    # INPUT:   techs = List of technologies to print over
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #This one is easier to manually do...
    outData = []

    # unit conversion from GWyr to PJ
    # 1 GW (1 TW / 1000 GW)*(1 PW / 1000 TW)*(8760 hrs / yr)*(3600 sec / 1 hr) = 31.536
    # If 1 GW of capacity works constantly throughout the year, it produced 31.536 PJ
    capToAct = 31.536

    #Technologies to print over
    df = pd.read_csv('../src/data/USA/TECHNOLOGY.csv')
    techs = df['VALUE'].tolist()

    #populate list
    for tech in techs:
        outData.append(['NAmerica', tech, capToAct])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION','TECHNOLOGY', 'VALUE'])
    return dfOut

def getCapacityFactor(techMap, df):
    # PURPOSE: Creates capacityFactor file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #capacity factor only specified for 2015 and 2016
    #df = df.loc[df['YEAR'] == 2016]
    #df.reset_index()

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)
    df = dfFiltered
    df.reset_index()

    #years to print capacity factor over
    years = range(2019,2051)

    #holds output data
    outDataCF = [] # Capacity Factor
    outDataAF = [] # Availability Factor

    #map data
    for year in years:
        for i in range(len(df)):
            region = 'NAmerica'
            techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
            ts = df['TIMESLICE'].iloc[i]
            value = df['CAPACITYFACTOR'].iloc[i]
            if techMapped == 'HYD':
                outDataAF.append([region,tech,ts,year,value])
            else:
                outDataCF.append([region,tech,ts,year,value])

    #create and return dataframe for CAPACITY FACTOR
    dfOutCF = pd.DataFrame(outDataCF, columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])

    #Create and write Availability Factor data to a dataframe 
    dfAf = pd.DataFrame(outDataAF, columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    afTechs = dfAf['TECHNOLOGY'].to_list()
    afTechs = list(set(afTechs))

    outDataAF = [] 
    for tech in afTechs:
        dfTemp = dfAf.loc[dfAf['TECHNOLOGY'] == tech]
        for year in years:
            dfYear = dfTemp.loc[dfTemp['YEAR'] == year]
            af = dfYear['VALUE'].mean()
            outDataAF.append(['NAmerica',tech,year,af])
    
    #create and return dataframe for CAPACITY FACTOR
    dfOutAF = pd.DataFrame(outDataAF, columns = ['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfOutAF.to_csv('../src/data/USA/AvailabilityFactor.csv', index=False)
        
    return dfOutCF

def getOperationalLife(techMap, df):
    # PURPOSE: Creates opertionalLife file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

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
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        value = df['OPERATIONALLIFE'].iloc[i]
        outData.append([region,tech,value])

    #Transmission operational life 
    dfTrade = pd.read_csv('../dataSources/USA_Trade.csv')
    techListTrade = dfTrade['TECHNOLOGY'].tolist()
    techListTrade = list(set(techListTrade)) #remove duplicates
    for tech in techListTrade:
        outData.append(['NAmerica',tech,100])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','VALUE'])
    return dfOut

def getResidualCapacity(techMap, df):
    # PURPOSE: Creates residualCapacity file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

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
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['RESIDUALCAPACITY'].iloc[i]
        outData.append([region,tech,year,value])

    #Transmission Residual Capacity
    dfTrade = pd.read_csv('../dataSources/USA_Trade.csv')
    techListTrade = dfTrade['TECHNOLOGY'].tolist()
    techListTrade = list(set(techListTrade)) #remove duplicates

    for region in ['NAmerica']:
      for tech in techListTrade:
        dfResCapTrd = dfTrade.loc[(dfTrade['TECHNOLOGY'] == tech) & 
                                  (dfTrade['MODE'] == 1)]
        dfResCapTrd.reset_index()
        resCapTrd = dfResCapTrd['CAPACITY (GW)'].iloc[0]
        for year in range(2019,2051):
          outData.append([region, tech, year, resCapTrd])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getInputActivityRatio(techMap, inputFuelMap, subregions, df):
    # PURPOSE: Creates inputActivityRatio file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #          inputFuelMap = dictionary mapping techs to fuels
    #          subregions = list of all subregions 
    #          df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)

    df = dfFiltered
    df.reset_index()    

    #Fuels that have international trade options
    intFuel = ['GAS','COA','URN']

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['INPUTACTIVITYRATIO'].iloc[i]
        fuelMapped = inputFuelMap[techMapped]

        #check if tech will operate on two modes of operation
        if fuelMapped in intFuel:
            fuel = fuelMapped + 'USA'
            outData.append([region,tech,fuel,1,year,value])
            fuel = fuelMapped + 'INT'
            outData.append([region,tech,fuel,2,year,value])
        else:
            fuel = fuelMapped + 'USA' + df['REGION'].iloc[i]
            outData.append([region,tech,fuel,1,year,value])

    #DONE IN CANADA SCRIPTS
    #Create input activity ration of international trade
    #for rawFuel in intFuel:
    #    for year in range(2019,2051):
    #        region = 'NAmerica'
    #        tech = 'MIN' + rawFuel + 'INT'
    #        fuel = rawFuel
    #        value = 1
    #        outData.append([region,tech,fuel,1,year,value])

    # IAR for PWRTRN technologies
    for subregion in subregions['USA']:
        for year in range(2019,2051):
            region = 'NAmerica'
            techName = 'PWR' + 'TRN' + 'USA' + subregion
            fuelIn = 'ELC' + 'USA' + subregion + '01'
            outData.append([region, techName, fuelIn, 1, year, 1])
    
    #IAR for transmission
    dfTrn = pd.read_csv('../dataSources/USA_Trade.csv')
    for region in ['NAmerica']:
        for year in range(2019,2051):
            for i in range(len(dfTrn)):
                techName = dfTrn.iloc[i]['TECHNOLOGY']
                inFuel = dfTrn.iloc[i]['INFUEL']
                iar = dfTrn.iloc[i]['IAR']
                mode = dfTrn.iloc[i]['MODE']
                outData.append([region, techName, inFuel, mode, year, iar])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

def getOutputActivityRatio(techMap, subregions):
    # PURPOSE: Creates outputActivityRatio file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #          subregions = list of all subregions 
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #Fuels that have international trade options
    intFuel = ['GAS','COA','URN']
    rnwFuel = ['HYD', 'SPV', 'WND', 'BIO']

    #holds output data
    outData = []

    #year to print over
    years = range(2019,2051)

    #renewables
    for year in years:
        for rawFuel in rnwFuel:
            for subregion in subregions['USA']:
                region = 'NAmerica'
                techName = 'RNW' + rawFuel + 'USA' + subregion
                fuel = rawFuel + 'USA' + subregion 
                outData.append([region, techName, fuel, 1, year, 1])

    #mining USA
    for year in years:
        for rawFuel in intFuel:
            region = 'NAmerica'
            techName = 'MIN' + rawFuel + 'USA'
            fuel = rawFuel + 'USA'
            outData.append([region, techName, fuel, 1, year, 1])

    # DONE IN CANADA SCRIPTS
    #mining internationl
    #for year in years:
    #    for rawFuel in intFuel:
    #        for subregion in subregions:
    #            region = 'NAmerica'
    #            techName = 'MIN' + rawFuel + 'INT'
    #            fuel = rawFuel + 'INT'
    #            outData.append([region, techName, fuel, 1, year, 1])

    # OAR for PWRTRN technologies
    for subregion in subregions['USA']:
        for year in years:
            region = 'NAmerica'
            techName = 'PWR' + 'TRN' + 'USA' + subregion
            fuel = 'ELC' + 'USA' + subregion + '02'
            outData.append([region, techName, fuel, 1, year, 1])

    # OAR for PWR technologies
    for year in years:
        for subregion in subregions['USA']:
            for tech in techMap:
                region = 'NAmerica'
                techName = 'PWR' + techMap[tech] + 'USA' + subregion + '01'
                fuel = 'ELC' + 'USA' + subregion + '01'
                outData.append([region, techName, fuel, 1, year, 1])
                if techMap[tech] in intFuel:
                    outData.append([region, techName, fuel, 2, year, 1])

    #OAR for transmission
    dfTrn = pd.read_csv('../dataSources/USA_Trade.csv')
    for region in ['NAmerica']:
        for year in range(2019,2051):
            for i in range(len(dfTrn)):
                techName = dfTrn.iloc[i]['TECHNOLOGY']
                outFuel = dfTrn.iloc[i]['OUTFUEL']
                oar = dfTrn.iloc[i]['OAR']
                mode = dfTrn.iloc[i]['MODE']
                outData.append([region, techName, outFuel, mode, year, oar])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

    return dfOut

def getCapitalCost(techMap, df):
    # PURPOSE: Creates capitalCost file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

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
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['CAPITALCOST'].iloc[i]
        #Convert from $/kW to M$/GW

        outData.append([region,tech,year,value])

    #Get trade costs
    dfCosts = pd.read_csv('../dataSources/USA_Trade.csv')

    #Cost data only populated on mode 1 data rows
    dfCosts = dfCosts.loc[dfCosts['MODE'] == 1]

    # get list of all the technologies
    techList = dfCosts['TECHNOLOGY'].tolist()

    #Regions to print over
    regions = ['NAmerica']

    #cost types to get data for
    costType = ['CAPEX']

    #populate data
    for region in regions:
        for tech in techList:

            #remove all rows except for our technology
            dfCostsFiltered = dfCosts.loc[dfCosts['TECHNOLOGY']==tech]
            dfCostsFiltered.reset_index()

            #reset costs
            trnCost = 0

            #get costs
            for cost in costType:
                trnCost = trnCost + float(dfCostsFiltered[cost].iloc[0])

            #save same value for all years 
            for year in range(2019,2051):
                outData.append([region,tech,year,trnCost])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getVariableCost(techMap, inputFuelMap, df):
    # PURPOSE: Creates variableCost file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #          inputFuelMap = dictionary mapping techs to fuels
    #          df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)

    df = dfFiltered
    df.reset_index()

    #Fuels that have international trade options
    intFuel = ['GAS','COA','URN']

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        mode = 1
        value = df['VARIABLECOST'].iloc[i]
        outData.append([region,tech,mode,year,value])
        #checks if need to write value for mode 2
        if inputFuelMap[techMapped] in intFuel:
            mode = 2
            outData.append([region,tech,mode,year,value])

    #Get trade costs
    dfCosts = pd.read_csv('../dataSources/USA_Trade.csv')

    #Cost data only populated on mode 1 data rows
    dfCosts = dfCosts.loc[dfCosts['MODE'] == 1]

    # get list of all the technologies
    techList = dfCosts['TECHNOLOGY'].tolist()

    #Regions to print over
    regions = ['NAmerica']

    #cost types to get data for
    costType = ['Variable O&M', 'Fuel']

    #populate data
    for region in regions:
        for tech in techList:

            #remove all rows except for our technology
            dfCostsFiltered = dfCosts.loc[dfCosts['TECHNOLOGY']==tech]
            dfCostsFiltered.reset_index()

            #reset costs
            trnCost = 0

            #get costs
            for cost in costType:
                trnCost = trnCost + float(dfCostsFiltered[cost].iloc[0])

            #save same value for all years 
            for year in range(2019,2051):
                outData.append([region,tech,year,trnCost])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

def getFixedCost(techMap, df):
    # PURPOSE: Creates FixedCost file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

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
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['FIXEDCOST'].iloc[i]
        outData.append([region,tech,year,value])

    #Get trade costs
    dfCosts = pd.read_csv('../dataSources/USA_Trade.csv')

    #Cost data only populated on mode 1 data rows
    dfCosts = dfCosts.loc[dfCosts['MODE'] == 1]

    # get list of all the technologies
    techList = dfCosts['TECHNOLOGY'].tolist()

    #Regions to print over
    regions = ['NAmerica']

    #cost types to get data for
    costType = ['Fixed O&M']

    #populate data
    for region in regions:
        for tech in techList:

            #remove all rows except for our technology
            dfCostsFiltered = dfCosts.loc[dfCosts['TECHNOLOGY']==tech]
            dfCostsFiltered.reset_index()

            #reset costs
            trnCost = 0

            #get costs
            for cost in costType:
                trnCost = trnCost + float(dfCostsFiltered[cost].iloc[0])

            #save same value for all years 
            for year in range(2019,2051):
                outData.append([region,tech,year,trnCost])


    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getTotalAnnualMaxCapacity(techMap, df):
    # PURPOSE: Creates totalAnnualMaxCapacity file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

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
    outData = []

    #map data
    for i in range(len(df)):
        region = 'NAmerica'
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['TOTALANNUALMAXCAPACITY'].iloc[i]
        outData.append([region,tech,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getReserveMarginTagTechnology(techMap, df):
    # PURPOSE: Creates getReserveMarginTagTechnology file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #          df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    # Due to our naming convention, we actually want to assign reserve margin value
    # to reservemargintagtechnology
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'ReserveMargin(r,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #list to hold output data
    outData=[]

    #populate data 
    for techOld in techMap:
        for i in range(len(df)):
            region = 'NAmerica'
            techMapped = techMap[techOld]
            tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
            year = df['YEAR'].iloc[i]
            value = df['RESERVEMARGIN'].iloc[i]
            outData.append([region,tech,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getReserveMarginTagFuel(techMap, df):
    # PURPOSE: Creates ReserveMarginTagFuel file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #          df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #list to hold output data
    outData=[]

    #populate data 
    for i in range(len(df)):
        region = 'NAmerica'
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['RESERVEMARGINTAGFUEL'].iloc[i]
        outData.append([region,fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','FUEL','YEAR','VALUE'])
    return dfOut

def getReserveMargin():
    # PURPOSE: Creates ReserveMargin file
    # INPUT:   none
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #this one is easier to manually do...
    outData = []

    for year in range(2019,2051):
        outData.append(['NAmerica',year,1])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','YEAR','VALUE'])
    return dfOut

def getRETagTechnology(subregions):
    # PURPOSE: Creates RETagTechnology file from USA data
    # INPUT:   none
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #easier to do this one manually 
    techs = ['HYD','WND','BIO','SPV']
    years = range(2019,2051)

    outData = []

    for year in years:
        for subregion in subregions['USA']:
            for tech in techs:
                region = 'NAmerica'
                techName = 'PWR' + tech + 'USA' + subregion + '01'
                outData.append([region, techName, year, 1])

    # create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getEmisionActivityRatio(techMap, inputFuelMap, df):
    # PURPOSE: Creates EmisionActivityRatio file from USA data
    # INPUT:   techMap =  dictionary mapping USA naming to our naming for technologies
    #                     df = raw data
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #Only defined for year 2015
    years = range(2019,2051)

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
    outData = []

    #Fuels that have international trade options
    intFuel = ['GAS','COA','URN']

    #map data
    for year in years:
        for i in range(len(df)):
            region = 'NAmerica'
            techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
            emission = df['EMISSION'].iloc[i]
            mode = 1
            value = df['EMISSIONACTIVITYRATIO'].iloc[i]
            outData.append([region,tech,emission,mode,year,value])
            #checks if need to write value for mode 2
            if inputFuelMap[techMapped] in intFuel:
                mode = 2
                outData.append([region,tech,emission,mode,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut



if __name__ == "__main__":
    main()