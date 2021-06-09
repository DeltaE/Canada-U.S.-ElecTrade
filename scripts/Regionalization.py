import pandas as pd
import os
import numpy as np
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted REGION set
    # INPUT: none
    # OUTPUT: none

    #list to hold output values
    dataOut = []

    #Dictionary for region to province mappings
    regions = defaultdict(list)

    # Read in regionalization file 
    df = pd.read_csv('../dataSources/Regionalization.csv')
    for i in range(len(df)):    
        region = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        regions[region].append(province)
    
    for region in regions:
        dataOut.append(region)

    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/REGION.csv', index=False)

if __name__ == "__main__":
    main()