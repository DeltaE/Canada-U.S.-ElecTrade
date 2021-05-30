import pandas as pd
import os
import numpy as np
import datetime
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted AvailabilityFactor.csv datafile for Hydro
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

    #Dictionary holds month to season Mapping 
    seasons = {
        'W':[1, 2, 3],
        'SP':[4, 5, 6],
        'S':[7, 8, 9],
        'F':[10, 11, 12]}

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Availability Factor Calculations
    ###########################################

    # Residual Hydro Capacity (GW), Total Generation (TWh), and hydro generation (TWh) per province in 2017
    inData = {
        'BC':  [15.407,  74.483,  66.510],
        'AB':  [1.218,   81.404,   2.050],
        'SAS': [0.867,   24.739,   3.862],
        'MAN': [5.461,   37.076,  35.991],
        'ONT': [9.122,  152.745,  39.492],
        'QC':  [40.438, 214.375, 202.001],
        'NB':  [0.968,   13.404,   2.583],
        'NL':  [6.762,   39.069,  36.715],
        'NS':  [0.370,   10.034,   0.849],
        'PEI': [0.000,    0.615,   0.000]}
    # Residual Capacity: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startYear=2017&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20170101
    # Generation Source: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startMonth=01&cubeTimeFrame.startYear=2017&cubeTimeFrame.endMonth=12&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20171201
  
    #calculate capacity factor for each province 
    af = {}
    for region in regions:
        generation = 0 #TWh
        capacity = 0 #TW
        #calcualte totals for region 
        for province in regions[region]:
            capacity = capacity + inData[province][0]
            generation = generation + inData[province][2]
        
        #save total capacity factor
        af[region] = (generation*(1000/8760))/capacity
    
    #set up output dataframe 
    df = pd.DataFrame(columns = ['REGION','TECHNOLOGY','YEAR','VALUE'])

    #Populate output dataframe 
    for year in years:
        print(f'Hydro {year}')
        for region in regions:
            newRow = {'REGION':region,'TECHNOLOGY':'HYD','YEAR':year,'VALUE':af[region]}
            df = df.append(newRow, ignore_index=True)

    ###########################################
    # Writing Availability Factor to File 
    ###########################################

    df.to_csv('../src/data/AvailabilityFactor.csv', index=False)

if __name__ == "__main__":
    main()
