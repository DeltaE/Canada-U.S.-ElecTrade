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

    #Region to loop over
    regions = ['CanW','CanMW','CanONT','CanQC','CanATL']

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Compile Emission Activity Ratio
    ###########################################

    #read in raw emission activity values
    dfRaw = pd.read_csv('../dataSources/EmissionActivityRatioByTechnology.csv', index_col=0)

    #list to hold all output values 
    dataOut = []

    #get list of technologies to print over
    techList = list(dfRaw)

    #print all values 
    for region in regions:
        for tech in techList:
            for year in years:
                activityRatio = dfRaw.loc[year,tech]
                dataOut.append([region, tech, 'CO2', 1, year, activityRatio])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION','YEAR','VALUE'])
    dfOut.to_csv('../src/data/EmissionActivityRatio.csv', index=False)

if __name__ == "__main__":
    main()