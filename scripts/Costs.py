import pandas as pd
import functions

####################################################
## ASSUMES ALL PROVINCES USE THE SAME COST VALUES ##
####################################################

def main():
    # PURPOSE: Creates otoole formatted Capital Costs AND Variable Costs AND Fixed Costs CSV
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    subregions = ((functions.openYaml().get('subregions_dictionary'))['CAN']).keys() # Canadian subregions
    years = functions.getYears()

    #Trigger used to print capital, fixed and variable costs one at a time
    for trigger in range(1,4):

        #Cost type
        if trigger == 1:
            costType = ['CAPEX']
            dfUsa = getUsaCapitalCost()
            outFile = 'CapitalCost.csv'
        elif trigger == 2:
            costType = ['Fixed O&M']
            dfUsa = getUsaFixedCost()
            outFile = 'FixedCost.csv'
        elif trigger == 3:
            costType = ['Variable O&M', 'Fuel']
            dfUsa = getUsaVariableCost()
            outFile = 'VariableCost.csv'
        else:
            print('Need to select a cost type. SCRIPT NOT RUN!')
            exit()

        ###########################################
        # Cost Calculations
        ###########################################

        #reads the NREL raw datafile and extracts costs
        dfNREL = read_NREL(costType, subregions, years)

        #Populate P2G and FC costs
        #dfP2gSystem = p2gSystem(costType, regions, subregions, years)

        #Populate Trade costs
        trade = tradeCosts(costType, years)

        ###########################################
        # Writing Cost to file
        ###########################################

        #append all csvs together
        if trigger == 3:
            df = pd.DataFrame(columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
        else:
            df = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
        df = df.append(dfNREL)
        #df = df.append(dfP2gSystem)
        df = df.append(trade)
        df = df.append(dfUsa)

        '''
        #add a mode of operation column for variable cost
        if outFile == 'VariableCost.csv':
            modeOperation = []
            for i in range(len(df)):
                modeOperation.append(1)
            df.insert(2,'MODE_OF_OPERATION',modeOperation,True)
        '''

        #Print capactiyFactor dataframe to a csv 
        outLocation = '../src/data/' + outFile
        df.to_csv(outLocation, index=False)


def read_NREL(costType, subregions, years):
    # PURPOSE: reads the NREL raw excel data sheet
    # INPUT:   costType: List holding how to filter core_metric_parameter column
    #          regions: List holding what regions to print values over
    #          subregions: List holding what subregions to print values over
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding cost values 

    region = functions.openYaml().get('regions')[0]

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
        'HYD':['Hydropower', 'NPD4'] ,
        'CCG': ['NaturalGas','CCHighCF'],
        'CTG': ['NaturalGas','CTHighCF'],
        'WND': ['LandbasedWind','LTRG4'], 
        'SPV': ['UtilityPV','KansasCity'],
        'URN': ['Nuclear'],
        'BIO': ['Biopower','Dedicated'],
    }

    # Dictionary for converting given units
    # CAPX: $/kW -> (1000*1000) -> $/GW -> (x10^-6) -> M$/GW
    # Fixed O&M: $/kW-yr -> $/kW -> (1000*1000) -> $/GW -> (x10^-6) -> M$/GW
    # Variable O&M: $/MWh -> ((1/3600)*1000*1000*1000) -> $/PJ -> (x10^-6) -> M$/PJ
    # Fuel: $/MMBtu -> ((1MMBtu/293.07kWh)*(1/3600)*1000*1000*1000*1000) -> $/PJ -> (x10^-6) -> M$/PJ
    unitConversion = {
        'CAPEX': 1,
        'Fixed O&M': 1,
        'Variable O&M': 0.277778,
        'Fuel': 0.94782058
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

    #apply cost type filtering (capital, fixed, variable)
    dfCost = pd.DataFrame(columns=list(dfFiltered))
    for cost in costType:
        dfTemp = dfFiltered.loc[dfFiltered['core_metric_parameter'] == cost]
        dfCost = dfCost.append(dfTemp)
    
    #List to hold all output data
    #columns = region, technology, year, value
    data = []

    #used for numerical indexing over columns shown in cost type for loop
    colNames = list(dfCost) 

    #Technologies that operate on two modes of operation 
    modeTwoTechs = ['CCG','CTG','COA','COC','URN']

    #Loop over regions and years 
    for subregion in subregions:
        for year in years:

            #filter based on years
            dfYear = dfCost.loc[dfCost['core_metric_variable'] == year]

            #loop over technologies that contribute to total cost 
            for tech, techFilter in technology.items():

                #Filter to get desired technology
                dfTech = dfYear
                for i in range(len(techFilter)): 
                    dfTech = dfTech.loc[dfTech[colNames[i+3]] == techFilter[i]]

                #reset total cost 
                totalCost=0

                # For variable costs, we need to add variable cost and fuel cost
                for cost in costType:
                    dfEnd = dfTech.loc[dfTech['core_metric_parameter'] == cost]

                    #There should only be one (capital/fixed) or two (variable) line items left at this point 
                    if len(dfEnd) > 1:
                        print(f'There are {len(dfTech)} rows in the {year} {tech} dataframe for {costType[0]}')
                        print('DATA NOT WRITTEN!')
                        exit()
                    elif len(dfEnd) < 1:
                        #print(f'{tech} has a {cost} cost of zero in {year} for the {region} region')
                        totalCost = totalCost
                    else:
                        #calculate total cost
                        #handels edge case of nuclear fuel cost given in $/MWh
                        #####################################################
                        ###### HARD CODED IN ALL FULE UNITS TO BE MWh #######
                        ###### UNIT CONSISTENCY ISSUE ON ATB          #######
                        #####################################################
                        if tech == 'URN' and cost == 'Fuel':
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion['Variable O&M']
                        elif tech == 'COA' and cost == 'Fuel':
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion['Variable O&M']
                        elif tech == 'COC' and cost == 'Fuel':
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion['Variable O&M']
                        elif tech == 'CCG' and cost == 'Fuel':
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion['Variable O&M']
                        elif tech == 'CTG' and cost == 'Fuel':
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion['Variable O&M']
                        else:
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion[cost]
                    
                    totalCost = round(totalCost,3)

                #construct technology name
                techName = 'PWR' + tech + 'CAN' + subregion + '01'

                # write data to output list
                # need to include a mode column for variable cost
                if costType[0] == 'Variable O&M':
                    if tech in modeTwoTechs:
                        modes = [1,2]
                    else:
                        modes = [1]
                    for mode in modes:
                        data.append([region,techName,mode,year,totalCost])
                else:
                    data.append([region, techName, year, totalCost])
                
    if costType[0] == 'Variable O&M':
        df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    else:
        df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])

    return df

def p2gSystem(costType, regions, subregions, years):
    # PURPOSE: populates power to gas AND fuel cell capital, fixed, OR variable costs 
    # INPUT:   costType: List holding what cost we are looking for (names sasme as NREL)
    #          regions: List holding what regions to print values over
    #          subregions: List holding what subregions to print values over
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding cost values 
    
    #read in excel file 
    sourceFile = '../dataSources/P2G_FC_Costs.xlsx'
    dfP2g = pd.read_excel(sourceFile, sheet_name='P2G',index_col=0)
    dfFc = pd.read_excel(sourceFile, sheet_name='FC',index_col=0)

    # list to hold values 
    dataP2g = []
    dataFc = []

    # populate lists 
    for region in regions:
        for year in years:
            for subregion in subregions:

                #reset costs
                p2gCost = 0
                fcCost = 0

                #get costs
                for cost in costType:
                    p2gCost = p2gCost + dfP2g.loc[year,cost]
                    fcCost = fcCost + dfFc.loc[year,cost]
                
                #create tech names
                p2gName = 'PWR' + 'P2G' + 'CAN' + subregion + '01'
                fcName = 'PWR' + 'FCL' + 'CAN' + subregion + '01'

                # save data
                if costType[0] == 'Variable O&M': #add in mode 1 
                    dataP2g.append([region, p2gName, 1, year, p2gCost])
                    dataFc.append([region, fcName, 1, year, fcCost])
                else:
                    dataP2g.append([region, p2gName, year, p2gCost])
                    dataFc.append([region, fcName, year, fcCost])
    
    #create a master list to hold all data 
    data = dataP2g
    data.extend(dataFc)

    #return completed dataframe
    if costType[0] == 'Variable O&M':
        df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    else:
        df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return df

def tradeCosts(costType, years):
    # PURPOSE: populates trade capital, fixed, OR variable costs 
    # INPUT:   costType: List holding what cost we are looking for (names sasme as NREL)
    #          regions: List holding what regions to print values over
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding cost values for trade 

    region = functions.openYaml().get('regions')[0]

    # Read in the trade csv file which contains costs
    df = pd.read_csv('../dataSources/Trade.csv')

    #Cost data only populated on mode 1 data rows
    df = df.loc[df['MODE'] == 1]

    # get list of all the technologies
    techList = df['TECHNOLOGY'].tolist()
    #techList = list(set(techList)) #remove duplicates

    #List to hold all output data 
    # columns = region, technology, year, value
    data = []

    #populate data
    for tech in techList:

        #remove all rows except for our technology
        costdf = df.loc[df['TECHNOLOGY']==tech]
        costdf.reset_index()

        #reset costs
        trnCost = 0

        #get costs
        for cost in costType:
            trnCost = trnCost + float(costdf[cost].iloc[0])

        #save same value for all years 
        if costType[0] == 'Variable O&M':
            for year in years:
                data.append([region,tech,1,year,trnCost])
                data.append([region,tech,2,year,trnCost])
        else:
            for year in years:
                data.append([region,tech,year,trnCost])

    if costType[0] == 'Variable O&M':
        dfOut = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    else:
        dfOut = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getUsaCapitalCost():
    # PURPOSE: Creates capitalCosts from USA data (excluding transmission)
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    region = functions.openYaml().get('regions')[0]
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'CapitalCost(r,t,y)')

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
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['CAPITALCOST'].iloc[i]
        value = round(value, 3)
        #Convert from $/kW to M$/GW

        outData.append([region,tech,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getUsaFixedCost():
    # PURPOSE: Creates FixedCost file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'FixedCost(r,t,y)')

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
        value = round(value, 3)
        outData.append([region,tech,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getUsaVariableCost():
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
    intFuel = functions.openYaml().get('mine_fuels')

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

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()