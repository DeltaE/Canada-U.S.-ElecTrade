import pandas as pd
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted AvailabilityFactor.csv datafile for Hydro
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary holds month to season Mapping 
    seasons = {
        'W':[1, 2, 3],
        'SP':[4, 5, 6],
        'S':[7, 8, 9],
        'F':[10, 11, 12]}

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
    for subregion in subregions:
        generation = 0 #TWh
        capacity = 0 #TW
        #calcualte totals for subregion 
        for province in subregions[subregion]:
            capacity = capacity + inData[province][0]
            generation = generation + inData[province][2]
        
        #save total capacity factor
        af[subregion] = (generation*(1000/8760))/capacity
    
    #list to save data to 
    #columns = region, technology, year, value
    outData = []

    #Populate output lsit 
    for year in years:
        print(f'Hydro {year}')
        for region in regions:
            for subregion in subregions:
                techName = 'RWN' + 'HYD' + 'CAN' + subregion + '01'
                outData.append([region, techName, year, af[subregion]])

    ###########################################
    # Writing Availability Factor to File 
    ###########################################

    df = pd.DataFrame(outData, columns = ['REGION','TECHNOLOGY','YEAR','VALUE'])
    df.to_csv('../src/data/AvailabilityFactor.csv', index=False)

if __name__ == "__main__":
    main()
