import pandas as pd

def main():
    # PURPOSE: Creates TEch and Fuel sets. Writes our files that are referenced by other scripts
    # INPUT: none
    # OUTPUT: none

    ####################################
    ## MODEL PARAMETERS
    ####################################

    # Model Name 
    model = ['Canada_USA']

    # Regions in the model
    regions = ['NAmerica']

    # Years to loop over 
    years = list(range(2019,2051,1))

    # Emission Types
    emissions = ['CO2']

    # PWR Technologies
    techsMaster = [
        'BIO', # Biomass
        'CCG', # Gas Combind Cycle 
        'CTG', # Gas Combustion Turbine
        'COA', # Coal
        'COC', # Coal CCS
        'HYD', # Hydro 
        'SPV', # Solar
        'URN', # Nuclear
        'WND', # Wind
        #'P2G', # Power to Gas
        #'FCL'  # Fuel Cell
    ]

    #RWN Technologies
    rnwTechs = [
        'HYD', # Hydro 
        'SPV', # Solar
        'WND', # Wind
        'BIO', # Biomass
    ]

    #MIN TEchnologies
    mineTechs = [
        'COA', # Coal
        'GAS', # Gas
        'URN', # Nuclear
    ]

    #STO Technologies
    stoTechs = [
        #'TNK' #Tank
    ]

    #Countries and subregions in the model
    countries = {
        'CAN':[] #Canada
        }

    #Read in subregions. This step is needed cause other scripts use the 
    #provincial breakdown by subregion in the excel file 
    sourceFile = '../dataSources/Regionalization.xlsx'
    for country in countries:
        dfCountry = pd.read_excel(sourceFile, sheet_name=country)
        regionList = dfCountry['REGION'].tolist()
        regionList = list(set(regionList)) # remove duplicates
        countries[country] = regionList # save to dictionary

    #######################################
    ## CREATE TECH LISTS FOR OTHER SCRIPTS
    #######################################
    
    data = []

    for i in range(len(techsMaster)):
        data.append(['PWR',techsMaster[i]])

    for i in range(len(rnwTechs)):
        data.append(['RNW',rnwTechs[i]])

    for i in range(len(mineTechs)):
        data.append(['MIN',mineTechs[i]])

    for i in range(len(stoTechs)):
        data.append(['STO',stoTechs[i]])

    dfGenerationType = pd.DataFrame(data, columns=['GENERATION','VALUE'])
    dfGenerationType.to_csv('../dataSources/techList_AUTO_GENERATED.csv', index = False)

    ####################################
    ## CREATE STANDARD SETS
    ####################################

    # Years set
    dfOut = pd.DataFrame(years,columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/YEAR.csv', index=False)

    #Regions set
    dfOut = pd.DataFrame(regions, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/REGION.csv', index=False)

    # Emissions set
    dfOut = pd.DataFrame(emissions, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/EMISSION.csv', index=False)

    ####################################
    ## CREATE STORAGE SET
    ####################################

    #get storages for each region 
    stoList = getSTO(countries, stoTechs)

    dfOut = pd.DataFrame(stoList, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/STORAGE.csv', index=False)

    ####################################
    ## CREATE TECHNOLOGY SET
    ####################################

    # get power generator technology list 
    pwrList = getPWRtechs(countries, techsMaster)

    # get grid distribution technology list (PWRTRN<Reg><SubReg>)
    pwrTrnList = getPWRTRNtechs(countries)

    # get Mining technology list
    minList = getMINtechs(countries, mineTechs)

    # get Renewables technology list 
    rnwList = getRNWtechs(countries, rnwTechs)

    # get trade technology list 
    trnList = getTRNtechs()

    #Append lists together and write to a csv
    outputTechs = pwrList + pwrTrnList + minList + rnwList + trnList
    dfOut = pd.DataFrame(outputTechs, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/TECHNOLOGY.csv', index=False)

    ####################################
    ## CREATE FUEL SET
    ####################################

    # Renewable fules
    rnwFuelList = getRNWfuels(countries, rnwTechs)

    # Mining fuels
    minFuelList = getMINfuels(countries, mineTechs)

    #ELC Fules
    elcFuelList = getELCfuels(countries)

    #Hydrogen Fuels
    #hy2FuelList = getHY2fuels(countries)

    #Append lists together and write to a csv
    #outputFuels = rnwFuelList + minFuelList + elcFuelList + hy2FuelList
    outputFuels = rnwFuelList + minFuelList  + elcFuelList
    dfOut = pd.DataFrame(outputFuels, columns=['VALUE'])
    dfOut.to_csv('../src/data/Canada/FUEL.csv', index=False)

    ####################################
    ## Extra Functions
    ####################################

def getPWRtechs(regions, techs):
    # PURPOSE: Creates all the PWR naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the PWR technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for tech in techs:
                techName = 'PWR' + tech + region + subregion + '01'
                outList.append(techName)
    
    # Return list of pwr Technologes
    return outList

def getPWRTRNtechs(regions):
    # PURPOSE: Creates all the PWRTRN naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the PWR technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
                techName = 'PWR' + 'TRN' + region + subregion
                outList.append(techName)
    
    # Return list of pwr Technologes
    return outList

def getMINtechs(regions, techs):
    # PURPOSE: Creates all the MIN naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the MIN technologies

    # list to hold technologies
    outList = []

    # Loop to create all regionalized technology names
    for region in regions:
        for tech in techs:
            techName = 'MIN' + tech + region
            outList.append(techName)
    
    # Loop to create all international mining techs
    for tech in techs:
        techName = 'MIN' + tech + 'INT'
        outList.append(techName)

    # Return list of min Technologes
    return outList

def getRNWtechs(regions, techs):
    # PURPOSE: Creates all the RNW naming technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the RNW technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for tech in techs:
                techName = 'RNW' + tech + region + subregion
                outList.append(techName)
    
    # Return list of rnw Technologes
    return outList

def getTRNtechs():
    # PURPOSE: Creates all the TRN naming technologies
    # INPUT:   None
    # OUTPUT:  outList =  List of all the TRN technologies

    # list to hold technologies
    outList = []

    #Read in the trade csv datafile 
    df = pd.read_csv('../dataSources/Trade.csv')
    outList = df['TECHNOLOGY'].tolist()
    outList = list(set(outList)) # remove duplicates
    
    # Return list of rnw Technologes
    return outList

def getRNWfuels(regions, techs):
    # PURPOSE: Creates fuels names for Renewable technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the RNW technologies

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for tech in techs:
                fuelName = tech + region + subregion
                outList.append(fuelName)
    
    # Return list of rnw fuels
    return outList

def getMINfuels(regions, techs):
    # PURPOSE: Creates Fuel names for Min technologies
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    #          techs =    List of the technologies to print over 
    # OUTPUT:  outList =  List of all the MIN Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names based on region
    for region in regions:
        for tech in techs:
            fuelName = tech + region
            outList.append(fuelName)
    
    # Loop to create all technology names for international import/export
    for tech in techs:
        fuelName = tech + 'INT'
        outList.append(fuelName)
    for tech in techs:
        outList.append(tech)

    # Return list of min TFuels
    return outList

def getELCfuels(regions):
    # PURPOSE: Creates Fuel electricity use fuel names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the ELC Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            elcOne = 'ELC' + region + subregion + '01'
            elcTwo = 'ELC' + region + subregion + '02'
            outList.extend([elcOne, elcTwo])
    
    # Return list of electricty fuels
    return outList

def getHY2fuels(regions):
    # PURPOSE: Creates Hydrogen Fuel names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the ELC Fuels 

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            fuelName = 'HY2' + region + subregion + '01'
            outList.append(fuelName)
    
    # Return list of hydrogen fuels
    return outList

def getSTO(regions, storages):
    # PURPOSE: Creates storage names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the STO names

    # list to hold technologies
    outList = []

    if not storages:
        return storages

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for storage in storages:
                storageName = 'STO' + storage + region + subregion
                outList.append(storageName)
    
    # Return list of hydrogen fuels
    return outList

if __name__ == "__main__":
    main()  