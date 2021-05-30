import pandas as pd
import os
import numpy as np
import datetime
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted SpecifiedAnnualDemand csv file 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary for region to province mappings
    regions = defaultdict(list)

    # Read in regionalization file 
    df = pd.read_csv('../dataSources/Regionalization.csv')
    for i in range(len(df)):    
        region = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        regions[region].append(province)

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Calculate demand  
    ###########################################

    #Read in csv containing data
    sourceFile = '../dataSources/ProvincialAnnualDemand.csv'
    df = pd.read_csv(sourceFile, index_col=0)

    #Master list to output
    #Region, fuel, year, value
    demand = []
    
    for region, provinces in regions.items(): 
        dfRegion = df[regions[region]]
        sumDemand = dfRegion.loc[:,:].sum(axis=1)
        for year in years:
            demand.append([region, 'ELC', year, sumDemand[year]])

    ###########################################
    # Writing Demand Files 
    ###########################################

    df = pd.DataFrame(demand, columns = ['REGION', 'FUEL', 'YEAR', 'VALUE'])
    df.to_csv('../src/data/SpecifiedAnnualDemand.csv', index=False)

if __name__ == "__main__":
    main()
