import pandas as pd
import functions

def main():
    # PURPOSE: Creates otoole formatted Emission Activity Ratio CSV 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ### EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1
    ### EVERYTHING IS CO2 EMISSIONS
    
    #write to a csv
    dataOut = getCanEmissionActivityRatio()
    dfUsa = getUsaEmissionActivityRatio()

    dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION','YEAR','VALUE'])
    dfOut = dfOut.append(dfUsa)
    dfOut.to_csv('../src/data/EmissionActivityRatio.csv', index=False)

def getCanEmissionActivityRatio():
    # PURPOSE: Creates EmissionActivityRatio file from Canadian data
    # INPUT:   N/A
    # OUTPUT:  dataOut = Canadian Emission Activity Ratio data

    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dict')['CAN'].keys() # Canadian subregions
    years = functions.getYears()

    #read in raw emission activity values
    dfRaw = pd.read_csv('../dataSources/EmissionActivityRatioByTechnology.csv', index_col=0)

    #list to hold all output values 
    dataOut = []

    #get list of technologies to print over
    techList = list(dfRaw)

    #Techs that operate on two modes of operation 
    modeTwoTechs = ['CCG','CCG','COA','COC','URN']

    #print all values 
    for year in years:
        for subregion in canSubregions:
            for tech in techList:
                activityRatio = dfRaw.loc[year,tech]
                activityRatio = round(activityRatio, 3)
                techName = 'PWR' + tech + 'CAN' + subregion + '01'
                dataOut.append([continent, techName, 'CO2', 1, year, activityRatio])
                if tech in modeTwoTechs:
                    dataOut.append([continent, techName, 'CO2', 2, year, activityRatio])
    
    return dataOut

def getUsaEmissionActivityRatio():
    # PURPOSE: Creates EmissionActivityRatio file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.getFromYaml('usa_tech_map')
    inputFuelMap = functions.getFromYaml('tech_to_fuel')
    continent = functions.getFromYaml('continent')
    intFuel = functions.getFromYaml('mine_fuels') # Fuels that have international trade options
    years = functions.getYears() # Only defined for year 2015

    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'EmisionActivityRatio(r,t,e,m,y)')

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
    for year in years:
        for i in range(len(df)):
            techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
            emission = df['EMISSION'].iloc[i]
            mode = 1
            value = df['EMISSIONACTIVITYRATIO'].iloc[i]
            value = round(value, 3)
            outData.append([continent,tech,emission,mode,year,value])
            #checks if need to write value for mode 2
            if inputFuelMap[techMapped] in intFuel:
                mode = 2
                outData.append([continent,tech,emission,mode,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()