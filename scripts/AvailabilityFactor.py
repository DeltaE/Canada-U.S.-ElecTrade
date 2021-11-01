import pandas as pd
import functions

def main():
    # PURPOSE: Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    seasons = functions.initializeSeasons()
    years = functions.initializeYears()
    regions = functions.initializeRegions()
    subregions = functions.initializeSubregions()

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
                techName = 'PWR' + 'HYD' + 'CAN' + subregion + '01'
                value = round(af[subregion],3)
                outData.append([region, techName, year, value])

    ###########################################
    # Writing Availability Factor to File 
    ###########################################

    df = pd.DataFrame(outData, columns = ['REGION','TECHNOLOGY','YEAR','VALUE'])
    df.to_csv('../src/data/Canada/AvailabilityFactor.csv', index=False)

if __name__ == "__main__":
    main()
