import pandas as pd
import os
import numpy as np
import datetime

def main():
    # PURPOSE: Creates otoole formatted SpecifiedAnnualDemand csv file 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary holds Provice to Region mapping 
    regions = {
        'CanW':['BC','AB'],
        'CanMW':['SAS','MAN'],
        'CanONT':['ONT'],
        'CanQC':['QC'],
        'CanATL':['NB','NS','PEI','NL']}

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
