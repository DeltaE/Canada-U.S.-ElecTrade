import pandas as pd

def main():
    # PURPOSE: Creates otoole formatted Emission Activity Ratio CSV 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    ### EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1
    ### EVERYTHING IS CO2 EMISSIONS

    # Regions to print over
    df = pd.read_csv('../src/data/Canada/REGION.csv')
    regions = df['VALUE'].tolist()

    # Subregions to print over
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    subregions = df['REGION'].tolist()
    subregions = list(set(subregions)) # removes duplicates

    #Years to Print over
    dfYears = pd.read_csv('../src/data/Canada/YEAR.csv')
    years = dfYears['VALUE'].tolist()

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
    dfOut.to_csv('../src/data/Canada/EmissionActivityRatio.csv', index=False)

if __name__ == "__main__":
    main()