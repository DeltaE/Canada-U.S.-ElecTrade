import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted input and output acitivy ratios
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ###EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #Years to Print over
    years = range(2019,2051,1)

    # Technology to Fuel Mapping for INPUT acticity ratio
    inputTechToFuel = {
        'HYD': 'Hydro_F',
        'WN': 'Wind_F',
        'BIO': 'Bio_F',
        'CL': 'Coal_F',
        'PV': 'Solar_F',
        'NUC':'Nuc_F',
        'FC':'H2',
        'P2G':'ELC',
        'NGCT':'NG_F',
        'NGCC':'NG_F',
        'CLCCS': 'Coal_F',
        'OI':'Oil_F',
    }

    # Technology to Fuel Mapping for OUTPUT acticity ratio
    outputTechToFuel = {
        'HYD': 'ELC',
        'WN': 'ELC',
        'BIO': 'ELC',
        'CL': 'ELC',
        'PV': 'ELC',
        'NUC':'ELC',
        'FC':'ELC',
        'P2G':'H2',
        'NGCT':'ELC',
        'NGCC':'ELC',
        'CLCCS': 'ELC',
        'OI':'ELC',
        'MIN_HYD': 'Hydro_F',
        'MIN_WN': 'Wind_F',
        'MIN_BIO': 'Bio_F',
        'MIN_CL': 'Coal_F',
        'MIN_PV': 'Solar_F',
        'MIN_NUC': 'Nuc_F',
        'MIN_NG': 'NG_F',
        'MIN_OI': 'Oil_F'
    }

    ###########################################
    # Compile Activity Ratios
    ###########################################

    inFileNames = ['InputActivityRatioByTechnology.csv', 'OutputActivityRatioByTechnology.csv']
    outFileNames = ['InputActivityRatio.csv', 'OutputActivityRatio.csv']

    for i in range(len(inFileNames)):
    
        #read in raw operational life values
        dfRaw = pd.read_csv(f'../dataSources/{inFileNames[i]}', index_col=0)

        #get correct dictionary of techs -> fuels
        if outFileNames[i] == 'InputActivityRatio.csv':
            techToFuel = inputTechToFuel
        else:
            techToFuel = outputTechToFuel

        #list to hold all output values 
        dataOut = []

        #get list of technologies to print over
        techList = list(dfRaw)

        #print all values 
        for region in regions:
            for tech in techList:
                for year in years:
                    activityRatio = dfRaw.loc[year,tech]
                    fuel = techToFuel[tech]
                    dataOut.append([region, tech, fuel, 1, year, activityRatio])
        
        #write to a csv
        dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','FUEL','MODE_OF_OPERATION','YEAR','VALUE'])
        dfOut.to_csv(f'../src/data/{outFileNames[i]}', index=False)

if __name__ == "__main__":
    main()