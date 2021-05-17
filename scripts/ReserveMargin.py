import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted ReserveMargin, ReserveMarginTagFuel, and 
    #          ReserveMarginTagTechnology CSVs
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Region Dictionary
    # key holds region
    # value holds reserve margin
    regions = { 'W':1.15,
                'MW':1.42,
                'ME':1.15,
                'E':1.41 }

    #Years to Print over
    years = range(2019,2051,1)

    # List of fuels to tag
    fuelTag = ['ELC']

    # List of technologies to tag
    techTag = ['HYD','BIO','NGCC','NGCT','NUC','CL','CLCCS','FC']

    ###########################################
    # CREATE FILES
    ###########################################

    #reserve margin columns = Region, Year, Value
    reserveMargin = []

    #reserve margin Tag Fuel = Region, Fuel, Year, Value
    reserveMarginTagFuel = []

    #reserve margin Tag Technology = Region, Technology, Year, Value
    reserveMarginTagTech = []

    #populate lists 
    for region, rm in regions.items():
        for year in years:
            reserveMargin.append([region, year, rm])
            for fuel in fuelTag:
                reserveMarginTagFuel.append([region, fuel, year, 1])
            for tech in techTag:
                reserveMarginTagTech.append([region, tech, year, 1])

    #write to csvs
    dfReserveMargin = pd.DataFrame(reserveMargin,columns=['REGION','YEAR','VALUE'])
    dfReserveMargin.to_csv('../src/data/ReserveMargin.csv', index=False)

    dfReserveMarginFuel = pd.DataFrame(reserveMarginTagFuel,columns=['REGION','FUEL','YEAR','VALUE'])
    dfReserveMarginFuel.to_csv('../src/data/ReserveMarginTagFuel.csv', index=False)

    dfReserveMarginTech = pd.DataFrame(reserveMarginTagTech,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfReserveMarginTech.to_csv('../src/data/ReserveMarginTagTechnology.csv', index=False)

if __name__ == "__main__":
    main()  