import pandas as pd
import os
import numpy as np
import datetime

#Purpose: Take raw renewable.ninja CFs for Wind or Solar and generate otoole formatted CSVs based on the data

def main():

    #Get df for wind and solar data
    dfWind = renewableNinjaData('WIND')
    dfPV = renewableNinjaDat('PV')



def renewableNinjaData(tech):

    #Dictionary holds Provice to Region mapping 
    regions = {
        'W':['BC','AB'],
        'MW':['SAS','MAN'],
        'ME':['ONT','NB'],
        'E':['QC','NS','PEI','NL']}

    #TimeSlices to print over
    tsList = ['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24',
        'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12','F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24',
        'W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W14','W15','W16','W17','W18','W19','W20','W21','W22','W23','W24',
        'SP1','SP2','SP3','SP4','SP5','SP6','SP7','SP8','SP9','SP10','SP11','SP12','SP13','SP14','SP15','SP16','SP17','SP18','SP19','SP20','SP21','SP22','SP23','SP24']

    #Dictionary holds month to season Mapping 
    seasons = {
        'S':['07','08','09'],
        'F':['10','11','12'],
        'W':['01','02','03'],
        'SP':['04','05','06']}

    #Years to Print over
    years = [range(2019,2051,1)]

    #set up output dataframe 
    df = pd.DataFrame(columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])


def readRenewableNinjaCSV(csvName):

    #Path to file to read
    sourceFile = '..\\dataSources\\CapacityFactor\\' + csvName

    #read in file
    df = pd.read_csv(sourceFile, header=None)

    #drop first four rows and first column 
    df.drop([0,1,2,3])
    df.drop(0,axis=1)

    #add headers 
    df.columns = ['date','value']

    #add new columns to hold month, hour values 
    df[]






    
def readDemand():
    #Read Data Frame in and add column names
    csvName = 'Demand.csv'
    sourceFile = 'results' + '\\' + csvName
    df = pd.read_csv(sourceFile)
    columnsList = ['REGION','TIMESLICE','FUEL','YEAR','VALUE']
    df.columns = columnsList

    #return dataframe
    return df

# def readTrade():

    # #Read Data Frame in and add column names
    # csvName = 'Trade.csv'
    # sourceFile = 'results' + '\\' + csvName
    # df = pd.read_csv(sourceFile)
    # columnsList = ['REGION_FROM','REGION_TO','TIMESLICE','FUEL','YEAR','VALUE']
    # df.columns = columnsList

    # #return dataframe
    # return df




if __name__ == "__main__":
    main()
