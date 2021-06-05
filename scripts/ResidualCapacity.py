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

    # Regions to print over
    dfRegions = pd.read_csv('../src/data/REGION.csv')
    regions = dfRegions['VALUE'].tolist()

    #Dictionary for subregion to province mappings
    subregions = defaultdict(list)

    # Read in regionalization file to get provincial seperation
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    for i in range(len(df)):    
        subregion = df['REGION'].iloc[i]
        province = df['PROVINCE'].iloc[i]
        subregions[subregion].append(province)

    #Years to Print over
    dfYears = pd.read_csv('../src/data/YEAR.csv')
    years = dfYears['VALUE'].tolist()

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
      for subregion in subregions:
        for tech, value in opLife.items():
          techName = 'PWR' + tech + 'CAN' + subregion + '01'
          opLifeData.append([region,techName,value])

    # get trade tech names and save operational life values
    dfTrade = pd.read_csv('../dataSources/Trade.csv')

    # get list of all the trade technologies
    techListTrade = dfTrade['TECHNOLOGY'].tolist()
    techListTrade = list(set(techListTrade)) #remove duplicates

    # hardcode in operational life of 100 years 
    for region in regions:
      for tech in techListTrade:
        opLifeData.append([region,tech,100])

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
    for region in regions:
      for subregion, provinces in subregions.items():
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

              #create correct name
              techName = 'PWR' + tech + 'CAN' + subregion + '01'
              resCapData.append([region, techName, year, resCap])
    
    # get trade residual capacity -- we are assuming no capacity in transmission is being decommisioned 
    for region in regions:
      for tech in techListTrade:
        dfResCapTrd = dfTrade.loc[(dfTrade['TECHNOLOGY'] == tech) & 
                                  (dfTrade['MODE'] == 1)]
        dfResCapTrd.reset_index()
        resCapTrd = dfResCapTrd['CAPACITY (GW)'].iloc[0]
        for year in years:
          resCapData.append([region, tech, year, resCapTrd])

    #wrirte to a csv 
    dfOut = pd.DataFrame(resCapData,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfOut.to_csv('../src/data/ResidualCapacity.csv', index=False)

if __name__ == "__main__":
    main()
