import pandas as pd
import os
import numpy as np
from collections import defaultdict

def main():
    # PURPOSE: Creates otoole formatted operational life and residual capacity data CSVs. 
    #          The reason for creating both files is that Residual Capacity relies on operational life. 
    #          So if operational life is updates, residual capacity will also be updated. 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    #Dictionary for region to province mappings
    regions = defaultdict(list)

    # Read in regionalization file 
    df = pd.read_csv('../dataSources/Regionalization.csv')
    for i in range(len(df)):    
        region = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        regions[region].append(province)

    #Years to Print over
    years = range(2019,2051,1)

    ###########################################
    # Operational Life
    ###########################################

    #read in raw operational life values
    dfOperationalLife = pd.read_csv('../dataSources/OperationalLifeTechnology.csv')

    #Create a dictionary from the tech, year values for use with residual capacity 
    techs = dfOperationalLife['TECHNOLOGY'].tolist()
    opLifeYears = dfOperationalLife['YEARS'].tolist()
    opLife= {}
    for i in range(len(techs)):
        opLife[techs[i]] = opLifeYears[i]

    #List to hold output operational life values 
    #columns = region, technology, value
    opLifeData = []

    #save operational life to list
    for region in regions:
      for tech, value in opLife.items():
        opLifeData.append([region,tech,value])

    #write operational life to a csv
    dfOut = pd.DataFrame(opLifeData,columns=['REGION','TECHNOLOGY','VALUE'])
    dfOut.to_csv('../src/data/OperationalLife.csv', index=False)

    ###########################################
    # Residual Capacity
    ###########################################

    #read in raw operational life values
    dfResCap = pd.read_csv('../dataSources/ResidualCapacitiesByProvince.csv')

    #drop references column
    dfResCap.drop(['Ref_1','Ref_2'], axis=1, inplace=True)

    # update retirment column based on comission date and operational life 
    # if a user inputted number has been added, the retirement data is NOT updated 
    comissionList = dfResCap['COMISSION'].tolist()
    retirementList = dfResCap['RETIREMENT'].tolist()
    techList = dfResCap['TECHNOLOGY'].tolist()

    for i in range(len(techList)):
      if retirementList[i] == 0:
        retirementList[i] = comissionList[i] + opLife[techList[i]]

    #Update retirement column 
    dfResCap['RETIREMENT']=retirementList

    # list to hold residual capacity values
    # columns = Region, Technology, Year, Value
    resCapData = []

    #populate data list 
    for region, provinces in regions.items():
      dfProvince = pd.DataFrame() #Reset dataframe
      for province in provinces:
        dfTemp = dfResCap.loc[dfResCap['PROVINCE'] == province]
        dfProvince = dfProvince.append(dfTemp, ignore_index=True)
      for tech in techs:
        for year in years:
            dfFiltered = dfProvince.loc[(dfProvince['TECHNOLOGY'] == tech) &
                                        (dfProvince['RETIREMENT'] >= year) &
                                        (dfProvince['COMISSION'] <= year) ]
            resCap = dfFiltered['CAPACITY (MW)'].sum()
            resCap = resCap / 1000 #MW -> GW
            resCapData.append([region, tech, year, resCap])

    #wrirte to a csv 
    dfOut = pd.DataFrame(resCapData,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfOut.to_csv('../src/data/ResidualCapacity.csv', index=False)

if __name__ == "__main__":
    main()
