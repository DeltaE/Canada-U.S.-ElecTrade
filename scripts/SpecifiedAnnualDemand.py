import pandas as pd
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted SpecifiedAnnualDemand csv file 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Years to Print over
    dfYears = pd.read_csv('../src/data/YEAR.csv')
    years = dfYears['VALUE'].tolist()

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

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
                demand.append([region, fuelName, year, sumDemand[year]])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(demand, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    df.to_csv('../src/data/SpecifiedAnnualDemand.csv', index=False)

if __name__ == "__main__":
    main()
