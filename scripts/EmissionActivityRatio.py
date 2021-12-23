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

    # Parameters to print over
    regions = functions.openYaml().get('regions')
    subregions = (functions.openYaml().get('subregions_dictionary')).keys()
    years = functions.getYears()

    ###########################################
    # Compile Emission Activity Ratio
    ###########################################

    #read in raw emission activity values
    dfRaw = pd.read_csv('../dataSources/EmissionActivityRatioByTechnology.csv', index_col=0)

    #list to hold all output values 
    dataOut = []

    #get list of technologies to print over
    techList = list(dfRaw)

    #Techs that operate on two modes of operation 
    modeTwoTechs = ['CCG','CCG','COA','COC','URN']

    #print all values 
    for region in regions:
        for year in years:
            for subregion in subregions:
                for tech in techList:
                    activityRatio = dfRaw.loc[year,tech]
                    activityRatio = round(activityRatio, 3)
                    techName = 'PWR' + tech + 'CAN' + subregion + '01'
                    dataOut.append([region, techName, 'CO2', 1, year, activityRatio])
                    if tech in modeTwoTechs:
                        dataOut.append([region, techName, 'CO2', 2, year, activityRatio])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION','YEAR','VALUE'])
    dfUsa = getUsaEmissionActivityRatio()
    dfOut = dfOut.append(dfUsa)
    dfOut.to_csv('../src/data/EmissionActivityRatio.csv', index=False)

def getUsaEmissionActivityRatio():
    # PURPOSE: Creates EmissionActivityRatio file from USA data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    techMap = functions.openYaml().get('usa_tech_map')
    inputFuelMap = functions.openYaml().get('tech_to_fuel')
    df = pd.read_excel('../dataSources/USA_Data.xlsx', sheet_name = 'EmisionActivityRatio(r,t,e,m,y)')

    #Only defined for year 2015
    years = functions.getYears()

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

    #Fuels that have international trade options
    intFuel = functions.openYaml().get('mine_techs')

    #map data
    for year in years:
        for i in range(len(df)):
            region = 'NAmerica'
            techMapped = techMap[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + techMapped + 'USA' + df['REGION'].iloc[i] + '01'
            emission = df['EMISSION'].iloc[i]
            mode = 1
            value = df['EMISSIONACTIVITYRATIO'].iloc[i]
            value = round(value, 3)
            outData.append([region,tech,emission,mode,year,value])
            #checks if need to write value for mode 2
            if inputFuelMap[techMapped] in intFuel:
                mode = 2
                outData.append([region,tech,emission,mode,year,value])

    #create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()