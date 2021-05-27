import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted emission activity ratio csv
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ### EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1
    ### EVERYTHING IS CO2 EMISSIONS

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Compile Emission Activity Ratio
    ###########################################

    #read in raw emission activity values
    dfRaw = pd.read_csv('../dataSources/EmissionPenaltyByYear.csv', index_col=0)

    #list to hold all output values
    #columns = region, emission, year, value
    dataOut = []

    #print all values 
    for region in regions:
        for year in years:
            penalty = dfRaw.loc[year,'PENALTY (M$/Mtonne)']
            dataOut.append([region, 'CO2', year, penalty])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','EMISSION','YEAR','VALUE'])
    dfOut.to_csv('../src/data/EmissionsPenalty.csv', index=False)

if __name__ == "__main__":
    main()