#####################################
## This file is for retrieving all USA information
#####################################

import pandas as pd
import functions

def getVariableCost():
    # PURPOSE: Creates variableCost file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    inputFuelMap = functions.openYaml().get('tech_to_fuel')
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'VariableCost(r,t,m,y)')

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
        value = round(value, 3)
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
            trnCost = round(trnCost, 3)

            #save same value for all years 
            for year in range(2019,2051):
                outData.append([region,tech,1,year,trnCost])
                outData.append([region,tech,2,year,trnCost])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

def getTotalAnnualMaxCapacity():
    # PURPOSE: Creates TotalAnnualMaxCapacity header data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    dfOut = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getSpecifiedDemandProfile():
    # PURPOSE: Creates specifiedDeamandProfile file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedDemandProfile(r,f,l,y)')

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
        value = round(value,3)
        outData.append([region,fuel,ts,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    return dfOut

def getSpecifiedAnnualDemand():
    # PURPOSE: Creates specifiedAnnualDemand file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'SpecifiedAnnualDemand(r,f,y)')

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
        value = round(value,3)
        outData.append([region,fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    return dfOut

def getRETagTechnology():
    # PURPOSE: Creates RETagTechnology file from USA data
    # INPUT:   none
    # OUTPUT:  dfOut = dataframe to be written to a csv

    dummy, regions, emissions, techsMaster, rnwTechs, mineTechs, stoTechs, subregions = functions.initializeCanadaUsaModelParameters('USA')

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

def getResidualCapacity():
    # PURPOSE: Creates residualCapacity file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'ResidualCapacity(r,t,y)')

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
        value = round(value,3)
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
        resCapTrd = round(float(resCapTrd),3)
        for year in range(2019,2051):
          outData.append([region, tech, year, resCapTrd])

    #create and return dataframe
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getReserveMarginTagTechnology():
    # PURPOSE: Creates getReserveMarginTagTechnology file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'ReserveMarginInTagTech(r,t,y)')

    techMap = functions.openYaml().get('usa_tech_map')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #list to hold output data
    outData=[]

    #get list of regions
    subregions = df['REGION']
    subregions = list(set(subregions))

    #populate data 
    for techOld in techMap:
        for year in range(2019,2051):
            for subregion in subregions:
                region = 'NAmerica'
                techMapped = techMap[techOld]
                tech = 'PWR' + techMapped + 'USA' + subregion + '01'
                if (techMapped == 'WND') or (techMapped == 'SPV'):
                    value = 0
                else:
                    value = 1
                outData.append([region,tech,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getReserveMarginTagFuel():
    # PURPOSE: Creates ReserveMarginTagFuel file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    # Due to our naming convention, we actually want to assign reserve margin value
    # to reservemargintagfuel

    # List of technologies to tag
    techTags = ['HYD','BIO','CCG','CTG','URN','COA','COC']

    ##################################################
    # Account for peak squishing 
    ##################################################
    # Region Dictionary
    regions = {
        'NW':['WA','OR'],
        'CA':['CA'],
        'MN':['MT','ID','WY','NV','UT','CO'],
        'SW':['AZ','NM'],
        'CE':['ND','SD','NE','KS','OK'],
        'TX':['TX'],
        'MW':['MN','WI','IA','IL','IN','MI','MO'],
        'AL':['AR','LA'],
        'MA':['OH','PA','WV','KY','VA','NJ','DE','MD'],
        'SE':['TN','NC','SC','MS','AL','GA'],
        'FL':['FL'],
        'NY':['NY'],
        'NE':['VT','NH','ME','MA','CT','RI'],
        }

    # Should update this for individual states
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

    #Fill in ovelap;ping regons (these will have the same reserve margin)
    dfProfile = dfProfile.drop(columns=['CAR Demand (MWh)'])
    dfProfile['MN'] = dfProfile['NW']

    #Get total annual demand 
    annualDemand = dict()
    for region, states in regions.items():
        regionalDemand = 0
        for state in states:
            regionalDemand = regionalDemand + dfDemand.loc[dfDemand['Abr.']==state]['PJ'].sum()
        if state == 'NY': #DC not by default included in demand 
            regionalDemand = regionalDemand + dfDemand.loc[dfDemand['Abr.']=='DC']['PJ'].sum()
        annualDemand[region] = regionalDemand

    #Normalize the load profiles 
    maxDemandDict = dict()
    for region in regions:
        maxDemand = dfProfile[region].max()
        totalDemand = dfProfile[region].sum()
        maxDemandDict[region] = maxDemand / totalDemand

    # Actual Peak Demand
    actualPeak = dict()
    for region in regions:
        actualPeak[region] = maxDemandDict[region] * annualDemand[region]

    #Modeled peak Demand
    dfModeledProfile = pd.read_excel('../dataSources/USA_Data.xlsx','SpecifiedDemandProfile(r,f,l,y)')

    #remove everything except 2019
    dfModeledProfile = dfModeledProfile.loc[(dfModeledProfile['YEAR'] > 2018) &
                                            (dfModeledProfile['YEAR']< 2020)]
    dfModeledProfile.reset_index()

    #get max modelled peak 
    modelledPeak = dict()
    for region in regions:
        maxProfile = dfModeledProfile.loc[(dfModeledProfile['REGION'] == region)]['DEMAND'].max()
        modelledPeak[region]=maxProfile * annualDemand[region] * (96/8960)

    #calculate adjusted reserve margin 
    reserveMargin = dict()
    for region in regions:
        reserveMargin[region] = baseRM[region] + (actualPeak[region] - modelledPeak[region]) / actualPeak[region]

    #list to hold output data
    outData=[]

    #populate data 
    for year in range(2019,2051):
        for region in regions:
            fuel = 'ELC' + 'USA' + region + '01'
            value = reserveMargin[region]
            outData.append(['NAmerica',fuel,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','FUEL','YEAR','VALUE'])
    return dfOut

def getReserveMargin():
    # PURPOSE: Creates ReserveMargin file
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    #this one is easier to manually do...
    outData = []

    for year in range(2019,2051):
        outData.append(['NAmerica',year,1])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','YEAR','VALUE'])
    return dfOut

def getOutputActivityRatio():
    # PURPOSE: Creates outputActivityRatio file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    dummy, regions, emissions, techsMaster, rnwTechs, mineTechs, stoTechs, subregions = functions.initializeCanadaUsaModelParameters('USA')

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

def getInputActivityRatio():
    # PURPOSE: Creates inputActivityRatio file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'InputActivityRatio(r,t,f,m,y)')
    techMap = functions.openYaml().get('usa_tech_map')
    dummy, regions, emissions, techsMaster, rnwTechs, mineTechs, stoTechs, subregions = functions.initializeCanadaUsaModelParameters('USA')
    inputFuelMap = functions.openYaml().get('tech_to_fuel')

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
        value = round(value, 3)
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