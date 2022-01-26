import pandas as pd
import os
import numpy as np
from collections import defaultdict
import functions

def main():
    # PURPOSE: Creates otoole formatted operational life and residual capacity data CSVs.  
    #          The reason for creating both files is that Residual Capacity relies on operational life. 
    #          So if operational life is updates, residual capacity will also be updated. 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dictionary')['CAN'] # Canadian subregions
    years = functions.getYears()

    ###########################################
    # Operational Life
    ###########################################

    #read in raw operational life values
    dfOperationalLife = pd.read_csv('../dataSources/OperationalLifeTechnology.csv')

    #remove P2G and FCL columns 
    rowsToDrop = []
    for i in range(len(dfOperationalLife)):
      tech = dfOperationalLife['TECHNOLOGY'].iloc[i]
      if (tech == 'P2G') or (tech == 'FCL'):
        rowsToDrop.append(i)
    dfOperationalLife = dfOperationalLife.drop(rowsToDrop)
    dfOperationalLife.reset_index()

    #Create a dictionary from the tech, year values for use with residual capacity 
    techs = dfOperationalLife['TECHNOLOGY'].tolist()
    opLifeYears = dfOperationalLife['YEARS'].tolist()
    opLife = {}
    for i in range(len(techs)):
        opLife[techs[i]] = opLifeYears[i]

    #List to hold output operational life values 
    #columns = region, technology, value
    opLifeData = []

    #save operational life to list
    for subregion in canSubregions:
      for tech, value in opLife.items():
        techName = 'PWR' + tech + 'CAN' + subregion + '01'
        opLifeData.append([continent,techName,value])

    # get trade tech names and save operational life values
    dfTrade = pd.read_csv('../dataSources/Trade.csv')

    # get list of all the trade technologies
    techListTrade = dfTrade['TECHNOLOGY'].tolist()
    techListTrade = list(set(techListTrade)) #remove duplicates

    # hardcode in operational life of 100 years 
    for tech in techListTrade:
      opLifeData.append([continent,tech,100])

    #write operational life to a csv
    dfOut = pd.DataFrame(opLifeData,columns=['REGION','TECHNOLOGY','VALUE'])
    dfOutUsa = getUsaOperationalLife()
    dfOut = dfOut.append(dfOutUsa)
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
    for subregion, provinces in canSubregions.items():
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
            resCap = round(resCap,3)

            #create correct name
            techName = 'PWR' + tech + 'CAN' + subregion + '01'
            resCapData.append([continent, techName, year, resCap])
    
    # get trade residual capacity -- we are assuming no capacity in transmission is being decommisioned 
    for tech in techListTrade:
      dfResCapTrd = dfTrade.loc[(dfTrade['TECHNOLOGY'] == tech) & 
                                (dfTrade['MODE'] == 1)]
      dfResCapTrd.reset_index()
      resCapTrd = dfResCapTrd['CAPACITY (GW)'].iloc[0]
      resCapTrd = round(float(resCapTrd),3)
      for year in years:
        resCapData.append([continent, tech, year, resCapTrd])

    #wrirte to a csv 
    dfOut = pd.DataFrame(resCapData,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfUsa = getUsaResidualCapacity()
    dfOut = dfOut.append(dfUsa)
    dfOut.to_csv('../src/data/ResidualCapacity.csv', index=False)

def getUsaResidualCapacity():
    # PURPOSE: Creates residualCapacity file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.getFromYaml('usa_tech_map')
    continent = functions.getFromYaml('continent')

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'ResidualCapacity(r,t,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)

    df = dfFiltered
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['RESIDUALCAPACITY'].iloc[i]
        value = round(value,3)
        outData.append([continent,tech,year,value])

    #create and return dataframe
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

def getUsaOperationalLife():
    # PURPOSE: Creates opertionalLife file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    continent = functions.getFromYaml('continent')
    techMap = functions.getFromYaml('usa_tech_map')
    
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'OperationalLife(r,t)')

    #Initialize filtered dataframe 
    columns = list(df)
    dfFiltered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using 
    for tech in techMap:
        dfTemp = df.loc[df['TECHNOLOGY'] == tech]
        dfFiltered = dfFiltered.append(dfTemp)

    df = dfFiltered
    df.reset_index()

    #holds output data
    outData = []

    #map data
    for i in range(len(df)):
        techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
        value = df['OPERATIONALLIFE'].iloc[i]
        outData.append([continent,tech,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()
