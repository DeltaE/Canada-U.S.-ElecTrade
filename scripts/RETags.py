import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted RETagTechnology
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #Years to Print over
    years = range(2019,2051,1)

    #Techs to tag
    techs = ['HYD','WN','BIO','PV']

    ###########################################
    # Compile RE Tags
    ###########################################

    #list to hold all output values
    #columns = region, emission, year, value
    dataOut = []

    #print all values 
    for region in regions:
        for tech in techs:
            for year in years:
                dataOut.append([region, tech, year, 1])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfOut.to_csv('../src/data/RETagTechnology.csv', index=False)

if __name__ == "__main__":
    main()