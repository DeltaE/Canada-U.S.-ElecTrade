import pandas as pd
import os
import numpy as np
import functions

def main():
    # PURPOSE: Creates otoole formatted EmissionsPenalty CSV  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    continent = functions.openYaml().get('continent')
    years = functions.getYears()

    ###########################################
    # Compile Emission Activity Ratio
    ###########################################

    #read in raw emission activity values
    dfRaw = pd.read_csv('../dataSources/EmissionPenaltyByYear.csv', index_col=0)

    #list to hold all output values
    #columns = region, emission, year, value
    dataOut = []

    #print all values 
    for year in years:
        penalty = dfRaw.loc[year,'PENALTY (M$/Mtonne)']
        dataOut.append([continent, 'CO2', year, penalty])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','EMISSION','YEAR','VALUE'])
    dfOut.to_csv('../src/data/EmissionsPenalty.csv', index=False)

if __name__ == "__main__":
    main()