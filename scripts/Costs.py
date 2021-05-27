import pandas as pd
import os
import numpy as np

####################################################
## ASSUMES ALL PROVINCES USE THE SAME COST VALUES ##
####################################################

def main():
    # PURPOSE: Creates otoole formatted Capital Costs OR Variable Costs OR FIxed Costs CSV
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    for trigger in range(1,4):

        #Years to Print over
        years = range(2019,2051,1)

        #Cost type
        if trigger == 1:
            costType = ['CAPEX']
            outFile = 'CapitalCost.csv'
        elif trigger == 2:
            costType = ['Fixed O&M']
            outFile = 'FixedCost.csv'
        elif trigger == 3:
            costType = ['Variable O&M', 'Fuel']
            outFile = 'VariableCost.csv'
        else:
            print('Need to select a cost type. SCRIPT NOT RUN!')
            exit()

        ###########################################
        # Cost Calculations
        ###########################################

        #reads the NREL raw datafile and extracts costs
        dfNREL = read_NREL(costType, regions, years)

        #Populate P2G and FC costs
        dfP2gSystem = p2gSystem(costType, regions, years)

        ###########################################
        # Writing Cost to file
        ###########################################

        #append all csvs together
        df = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
        df = df.append(dfNREL)
        df = df.append(dfP2gSystem)

        #add a mode of operation column for variable cost
        if outFile == 'VariableCost.csv':
            modeOperation = []
            for i in range(len(df)):
                modeOperation.append(1)
            df.insert(2,'MODE_OF_OPERATION',modeOperation,True)

        #Print capactiyFactor dataframe to a csv 
        outLocation = '../src/data/' + outFile
        df.to_csv(outLocation, index=False)


def read_NREL(costType, regions, years):
    # PURPOSE: reads the NREL raw excel data sheet
    # INPUT:   costType: List holding how to filter core_metric_parameter column
    #          regions: List holding what regions to print values over
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding cost values 

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
        'HYD':['Hydropower', 'NPD4'] ,
        'NGCC': ['NaturalGas','CCHighCF'],
        'NGCT': ['NaturalGas','CTHighCF'],
        'WN': ['LandbasedWind','LTRG4'], 
        'PV': ['UtilityPV','KansasCity'],
        'NUC': ['Nuclear'],
        'BIO': ['Biopower','Dedicated'],
    }

    # Dictionary for converting given units into $/GW or $/PJ
    # CAPX: $/kW -> $/GW (1000*1000)
    # Fixed O&M: $/kW-yr -> $/GW (1000*1000)
    # Variable O&M: $/MWh -> $/PJ ((1/3600)*1000*1000*1000)
    # Fuel: $/MMBtu -> $/PJ ((1MMBtu/293.07kWh)*(1/3600)*1000*1000*1000*1000)
    unitConversion = {
        'CAPEX': 1000000,
        'Fixed O&M': 1000000,
        'Variable O&M': 277777.8,
        'Fuel': 706687.8
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

    #Loop over regions and years 
    for region in regions:
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
                        if tech == 'NUC' and cost == 'Fuel':
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion['Variable O&M']
                        else:
                            totalCost = totalCost + dfEnd.iloc[0]['value']*unitConversion[cost]

                #write data to output list
                data.append([region, tech, year, totalCost])
                
    df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return df

def p2gSystem(costType, regions, years):
    # PURPOSE: populates power to gas AND fuel cell capital, fixed, OR variable costs 
    # INPUT:   costType: List holding what cost we are looking for (names sasme as NREL)
    #          regions: List holding what regions to print values over
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
            p2gCost = 0
            fcCost = 0
            for cost in costType:
                p2gCost = p2gCost + dfP2g.loc[year,cost]
                fcCost = fcCost + dfFc.loc[year,cost]
            dataP2g.append([region, 'P2G', year, p2gCost])
            dataFc.append([region, 'FC', year, fcCost])
    
    #create a dataframe to hold all data 
    data = dataP2g
    data.extend(dataFc)

    #return completed dataframe
    df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return df


def p2g(costType, regions, years):
    # PURPOSE: populates power to gas capital, fixed, or variable costs through hardcoded values
    # INPUT:   costType: List holding what cost we are looking for (names sasme as NREL)
    #          regions: List holding what regions to print values over
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding cost values 

    #get cost type to associate cost varaible to 
    if costType[0] == 'CAPEX':
        startCost = 1206000000 # $/GW
    elif costType[0] == 'Fixed O&M':
        startCost =100000 # $/GW
    else:
        variableCost = 0
        fuelCost = 0
        startCost = variableCost + fuelCost

    #List to hold all output data
    #columns = region, technology, year, value
    data = []

    for region in regions:
        cost = startCost
        for year in years:
            data.append([region,'P2G',year,cost])
            if costType[0] == 'CAPEX':
                cost = cost * 0.98 # 2% cost reduction per year
    
    df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return df

def fuelCell(costType, regions, years):
    # PURPOSE: populates power to gas capital, fixed, or variable costs through hardcoded values
    # INPUT:   costType: List holding what cost we are looking for (names sasme as NREL)
    #          regions: List holding what regions to print values over
    #          years: list holding what years to print data over
    # OUTPUT:  otoole formatted dataframe holding cost values 

    #get cost type to associate cost varaible to 
    if costType[0] == 'CAPEX':
        cost = 2400000000  # $/GW
    elif costType[0] == 'Fixed O&M':
        cost = 3600000000 * 0.02  # $/GW
    else:
        variableCost = 0
        fuelCost = 0
        cost = variableCost + fuelCost

    #List to hold all output data
    #columns = region, technology, year, value
    data = []

    for region in regions:
        for year in years:
            data.append([region,'FC',year,cost])

    df = pd.DataFrame(data, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return df

if __name__ == "__main__":
    main()