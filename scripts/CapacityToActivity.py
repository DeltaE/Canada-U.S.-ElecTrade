import pandas as pd
import os
import numpy as np

def main():
    # PURPOSE: Creates otoole formatted CapacityToActivityUnit.csv
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ## ASSUMES ALL CAPACITIES IN GW AND ALL ENNERGY IN PJ

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    # Techs to print over
    techs = ['HYD','WN','BIO','PV','NGCC','NGCT','NUC','CL','CLCCS','FC','P2G','OI']

    ###########################################
    # CREATE FILE
    ###########################################

    #capacity to activity columns = Region, Technology, Value
    data = []

    # unit conversion from GWyr to PJ
    # 1 GW (1 TW / 1000 GW)*(1 PW / 1000 TW)*(8760 hrs / yr)*(3600 sec / 1 hr) = 31.536
    # If 1 GW of capacity works constantly throughout the year, it produced 31.536 PJ
    capToAct = 31.536

    #populate list
    for region in regions:
        for tech in techs:
            data.append([region, tech, capToAct])

    #write to csv
    dfout = pd.DataFrame(data,columns=['REGION','TECHNOLOGY','VALUE'])
    dfout.to_csv('../src/data/CapacityToActivityUnit.csv', index=False)

if __name__ == "__main__":
    main()  