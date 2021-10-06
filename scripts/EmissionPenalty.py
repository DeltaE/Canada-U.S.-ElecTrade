import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted EmissionsPenalty CSV  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ### EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1
    ### EVERYTHING IS CO2 EMISSIONS

    # Regions to print over
    df = pd.read_csv('../src/data/Canada/REGION.csv')
    regions = df['VALUE'].tolist()

    #Years to Print over
    dfYears = pd.read_csv('../src/data/Canada/YEAR.csv')
    years = dfYears['VALUE'].tolist()

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
    dfOut.to_csv('../src/data/Canada/EmissionsPenalty.csv', index=False)

if __name__ == "__main__":
    main()