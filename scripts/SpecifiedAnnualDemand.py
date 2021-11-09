import pandas as pd
import functions
from collections import defaultdict

def main():
    # PURPOSE: Creates an otoole formatted CSV holding the specified annual demand for the model
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    years = functions.openYaml().get('years')
    regions = functions.openYaml().get('regions')

    #Dictionary for subregion to province mappings
    subregions = defaultdict(list)

    # Read in regionalization file to get provincial seperation
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    for i in range(len(df)):    
        subregion = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        subregions[subregion].append(province)

    ###########################################
    # Calculate demand  
    ###########################################

    #Read in csv containing data
    sourceFile = '../dataSources/ProvincialAnnualDemand.csv'
    df = pd.read_csv(sourceFile, index_col=0)

    #Master list to output
    #Region, fuel, year, value
    demand = []
    
    for region in regions:
        for subregion, provinces in subregions.items(): 
            dfRegion = df[subregions[subregion]]
            sumDemand = dfRegion.loc[:,:].sum(axis=1)
            for year in years:
                fuelName = 'ELC' + 'CAN' + subregion + '02'
                value = sumDemand[year]
                value = round(value,3)
                demand.append([region, fuelName, year, value])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(demand, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    df.to_csv('../src/data/Canada/SpecifiedAnnualDemand.csv', index=False)

if __name__ == "__main__":
    main()
