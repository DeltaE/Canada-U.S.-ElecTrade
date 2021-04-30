import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib import pyplot

def main():

    #Elements to plot over
    regionList = ['W','MW','ME','E']
    techList=['HYD', 'WN','BIO','GS','PV','CL','NUC','FC']
    fuelList=['ELC']
    colours = ['#22639c', '#209131','#ad151f' ,'#cc7416' ,'#d0d411', '#573875', '#00b87a', '#90109c', '#34a5c7']
    tsList = ['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12','F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24','W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W14','W15','W16','W17','W18','W19','W20','W21','W22','W23','W24','SP1','SP2','SP3','SP4','SP5','SP6','SP7','SP8','SP9','SP10','SP11','SP12','SP13','SP14','SP15','SP16','SP17','SP18','SP19','SP20','SP21','SP22','SP23','SP24']

    #read in dataframes
    dfProd = readProductionByTechnology()
    dfDemand = readDemand()

    #figure and axis
    fig, ax = plt.subplots(1,1)

    #will loop this later
    regionValue = 'W'
    #Create bar chart
    for year in range(2019,2051,1):
        for ts in tsList:
                #Filtered production df
                dfP = dfProd.loc[(dfProd.REGION == regionValue) & (dfProd.YEAR == year) & (dfProd.TIMESLICE == ts)]
                dfP.reset_index(drop=True, inplace=True)

                #create similar timeslice values for plotting. Will revert back later 
                xValue = f'{year}' +" " + ts

                #plot bars 
                bottom = 0 #tracks where stacked bar should start
                for idx, name in enumerate(techList):

                    dfP_Temp = dfP.loc[dfP.TECHNOLOGY == name]
                    dfP_Temp.reset_index(drop=True, inplace=True)
                    yValue = dfP_Temp.loc[0,'VALUE']

                    #yValue = dfP.loc[idx,'VALUE']
                    #print(f'{name} has value {yValue}')

                    #convert production in PJ to TW-h
                    yValue = yValue * (1/3600) * (1000)

                    #convert TW-h to TW by multiplying by hrs in timeslice 

                    yValue = yValue / ((365.25) * (0.01041666666) * (24))

                    #convert TW to GW
                    yValue = yValue * 1000
                    

                    plt.bar(xValue,yValue,bottom=bottom,color=colours[idx],width=1.0)
                    
                    bottom = bottom + yValue                  


    # title, legend, labels
    plt.title(f'Technology Production in {regionValue} Region\n', loc='center')
    legend1 = pyplot.legend(techList, frameon=False, loc='lower left', bbox_to_anchor=(1.0, 0.5))
    ax.add_artist(legend1)
    plt.xlabel('Year')
    plt.ylabel('Generation (GW)')

    #Create demand line

    xValues = []
    yValues = []
    for year in range(2019,2051,1):
        for ts in tsList:
                #Filtered demand df
                dfD = dfDemand.loc[(dfDemand.REGION == regionValue) & (dfDemand.YEAR == year) & (dfDemand.TIMESLICE == ts)]
                dfD.reset_index(drop=True, inplace=True)

                '''
                #get production of ELC2 to add to the yvalue 
                dfFC = dfProd.loc[(dfProd.REGION == regionValue) & (dfProd.YEAR == year) & (dfProd.TIMESLICE == ts) & (dfProd.TECHNOLOGY == 'FC')]
                dfFC.reset_index(drop=True, inplace=True)

                if dfFC.empty:
                    yValue = 0
                else:
                    yValue = dfFC.loc[0,'VALUE']
                '''
                yValue = 0

                #create similar timeslice values for plotting. Will revert back later 
                xValues.append(f'{year}' + " " + ts)

                #get demand value in PJ
                yValue = yValue + dfD.loc[0,'VALUE']
            
                #convert production in PJ to TW-h
                yValue = yValue * (1/3600) * (1000)

                #convert TW-h to TW by multiplying by hrs in timeslice 

                yValue = yValue / ((365.25) * (0.01041666666) * (24))

                #convert TW to GW
                yValue = yValue * 1000

                #store yvalue
                yValues.append(yValue)

    ax.plot(xValues, yValues, color='black')
    legend2 = pyplot.legend(["Demand"], frameon=False, loc='upper left', bbox_to_anchor=(1.0, 0.5))

    #keep only every 96th label (96 ts per year)
    n = 96
    for index, lable in enumerate(ax.xaxis.get_ticklabels()):
        
        if index % n != 0:
            lable.set_visible(False) 

    #change orientation of tick marks 
    plt.xticks(rotation = 90)

    #plt.xticks(np.arange(2019, 2051, 1.0))
    plt.show()


def readProductionByTechnology():
    #parameters to cycle over 
    regionList = ['W','MW','ME','E']
    techList=['HYD', 'WN','BIO','GS','PV','CL','NUC','TRD','FC']
    tsList = ['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12','F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24','W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W14','W15','W16','W17','W18','W19','W20','W21','W22','W23','W24','SP1','SP2','SP3','SP4','SP5','SP6','SP7','SP8','SP9','SP10','SP11','SP12','SP13','SP14','SP15','SP16','SP17','SP18','SP19','SP20','SP21','SP22','SP23','SP24']

    #Read Data Frame in and add column names
    csvName = 'ProductionByTechnology.csv'
    sourceFile = 'results' + '\\' + csvName
    df_raw = pd.read_csv(sourceFile)
    columnsList = ['REGION','TIMESLICE','TECHNOLOGY','FUEL','YEAR','VALUE']
    df_raw.columns = columnsList

    # #Filter out all trade technology that uses ELEC fuel (as ELC_TRD) is import fuel
    # df_tradeFilter = df_raw.loc[(df_raw['FUEL'] != 'ELC_TRD')]
    # df_tradeFilter = df_tradeFilter.loc[(df_tradeFilter['FUEL'] != 'H2')]

    # df_raw = df_tradeFilter

    #give a vlaue of zero to all ELC_TRD where required

    # for region in regionList:
        # for ts in tsList:
            # for year in range(2019,2051,1):
                # dfTemp = df_raw.loc[(df_raw['REGION'] == region) & (df_raw['TECHNOLOGY'] == 'TRD') & (df_raw['YEAR'] == year) & (df_raw['TIMESLICE'] == ts)]
                # dfTemp.reset_index(drop=True, inplace=True)

                # if dfTemp.empty:
                    # value = 0 #no production
                # else:
                    # continue

                # #save values for new row
                # newRow = {'REGION':region,'TIMESLICE':ts,'TECHNOLOGY':'TRD','FUEL':'ELC','YEAR':year,'VALUE':value}
                # df_raw = df_raw.append(newRow, ignore_index=True)

    #dataframe to hold compressed values
    df = pd.DataFrame(columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])

    #create main dataframe
    for region in regionList:
        for tech in techList:
            for year in range(2019,2051,1):
                for ts in tsList:
                    dfTemp = df_raw.loc[(df_raw['REGION'] == region) & (df_raw['TECHNOLOGY'] == tech) & (df_raw['YEAR'] == year) & (df_raw['TIMESLICE'] == ts)]
                    dfTemp.reset_index(drop=True, inplace=True)
                    
                    if dfTemp.empty:
                        value = 0 #no production
                    else:
                        value = dfTemp.at[0,'VALUE']

                    #save values for new row
                    newRow = {'REGION':region,'TECHNOLOGY':tech,'TIMESLICE':ts,'YEAR':year,'VALUE':value}
                    df = df.append(newRow, ignore_index=True)
    
    #df.to_csv('test.csv')

    return df

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
