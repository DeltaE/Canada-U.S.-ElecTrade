import pandas as pd
import functions

def main():
    # PURPOSE: Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    seasons = functions.openYaml().get('seasons')
    regions = functions.openYaml().get('regions')
    subregions = functions.openYaml().get('subregions_dictionary')
    years = functions.getYears()

    #####################################
    # CONSTANTS
    #####################################

    # Residual Hydro Capacity (GW) per province in 2017
    # Source: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startYear=2017&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20170101
    RESIDUAL_HYDRO_CAPACITY = {
    'BC':  15.407,
    'AB':  1.218,   
    'SAS': 0.867,   
    'MAN': 5.461,   
    'ONT': 9.122,   
    'QC':  40.438,  
    'NB':  0.968,   
    'NL':  6.762,   
    'NS':  0.370,   
    'PEI': 0.000}

    # Hydro generation (TWh) per province in 2017
    # Source: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startMonth=01&cubeTimeFrame.startYear=2017&cubeTimeFrame.endMonth=12&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20171201
    HYDRO_GENERATION = {
    'BC': 66.510,
    'AB': 2.050,
    'SAS': 3.862,
    'MAN': 35.991,
    'ONT': 39.492,
    'QC': 202.001,
    'NB': 2.583,
    'NL': 36.715,
    'NS': 0.849,
    'PEI': 0.000}

    ###########################################
    # Availability Factor Calculations
    ###########################################

    #calculate capacity factor for each province 
    af = {}
    for subregion in subregions:
        generation = 0 #TWh
        capacity = 0 #TW
        #calcualte totals for subregion 
        for province in subregions[subregion]:
            capacity = capacity + RESIDUAL_HYDRO_CAPACITY[province]
            generation = generation + HYDRO_GENERATION[province]
        
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
    dfUsa = functions.getUsaCapacityOrAvailabilityFactor(False)
    df = df.append(dfUsa)
    df.to_csv('../src/data/AvailabilityFactor.csv', index=False)

if __name__ == "__main__":
    main()
