import pandas as pd
import numpy as np
from pandas._libs import indexing
from pandas.core.indexes.base import Index

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

    # Storages
    storages = ['TNK'] #Tank

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
        'P2G', # Power to Gas
        'FCL'  # Fuel Cell
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
        'TNK' #Tank
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
    dfOut.to_csv('../src/data/YEAR.csv', index=False)

    #Regions set
    dfOut = pd.DataFrame(regions, columns=['VALUE'])
    dfOut.to_csv('../src/data/REGION.csv', index=False)

    # Emissions set
    dfOut = pd.DataFrame(emissions, columns=['VALUE'])
    dfOut.to_csv('../src/data/EMISSION.csv', index=False)

    ####################################
    ## CREATE STORAGE SET
    ####################################

    #get storages for each region 
    stoList = getSTO(countries, storages)

    dfOut = pd.DataFrame(stoList, columns=['VALUE'])
    dfOut.to_csv('../src/data/STORAGE.csv', index=False)

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
    dfOut.to_csv('../src/data/TECHNOLOGY.csv', index=False)

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
    hy2FuelList = getHY2fuels(countries)

    #Append lists together and write to a csv
    outputFuels = rnwFuelList + minFuelList + elcFuelList + hy2FuelList
    dfOut = pd.DataFrame(outputFuels, columns=['VALUE'])
    dfOut.to_csv('../src/data/FUEL.csv', index=False)

    ####################################
    ## WRITE PROVINCE TO REGION MAPPING
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

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            for storage in storages:
                storageName = 'STO' + storage + region + subregion
                outList.append(storageName)
    
    # Return list of hydrogen fuels
    return outList

'''

    LandRegions = ['JWA' , 'KAN', 'MLU', 'NUA', 'SLI', 'SMA', 'PPA']
    # LandRegions = ['IND']

    LandToGridMap = {
        'JWA': 'J',  # Java
        'KAN': 'K',  # Kalimantan
        'MLU': 'M',  # Maluku Islands
        'NUA': 'N',  # Lesser Sunda Islands
        'PPA': 'P',  # Western New Guinea
        'SLI': 'L',  # Sulawesi
        'SMA': 'S',   # Sumatra
    }


    # Energy Structure

    EndUseFuels = {
       'IND': ['COA', 'LPG', 'KER', 'DSL', 'HFO', 'OHC', 'BIO', 'NGS', 'ELCJ02', 'ELCK02', 'ELCM02', 'ELCN02', 'ELCP02', 'ELCL02', 'ELCS02'],
       'RES': ['LPG', 'KER', 'BIO', 'NGS', 'ELCJ02', 'ELCK02', 'ELCM02', 'ELCN02', 'ELCP02', 'ELCL02', 'ELCS02'],
       'COM': ['KER', 'DSL', 'LPG', 'BIO', 'NGS', 'ELCJ02', 'ELCK02', 'ELCM02', 'ELCN02', 'ELCP02', 'ELCL02', 'ELCS02'],
       'AGR': ['DSL', 'ELCJ02', 'ELCK02', 'ELCM02', 'ELCN02', 'ELCP02', 'ELCL02', 'ELCS02'],
       'TRA': ['GSL', 'KER', 'DSL', 'HFO', 'NGS', 'ELCJ02', 'ELCK02', 'ELCM02', 'ELCN02', 'ELCP02', 'ELCL02', 'ELCS02'],
       'OTH': ['CRU', 'KER', 'HFO', 'OHC', 'NGS', 'ELCJ02', 'ELCK02', 'ELCM02', 'ELCN02', 'ELCP02', 'ELCL02', 'ELCS02']
    }

    ImportFuels = ['COA', 'CRU', 'LPG', 'GSL', 'KER', 'DSL', 'HFO']

    ExportFuels = ['COA', 'NGS', 'CRU', 'GSL', 'KER', 'HFO', 'BIO']

    DomesticMining = ['COA', 'NGS', 'CRU']

    DomesticRenewables = ['WND', 'HYD', 'BIO', 'SOL', 'GEO']

    # Note:  Transformation technologies assume that their fuels are created elsewhere (either in the DomesticMining, DomesticRenewables or ImportFuels.
    TransformationTechnologies = [
        ['PWRTRNJ01', 'ELCJ01', '1.11', 'ELCJ02', '1', 'Power transmission Java', '1'],  # 90% efficient transmission system (losses)
    	['PWRTRNK01', 'ELCK01', '1.11', 'ELCK02', '1', 'Power transmission Kalimantan', '1'],
    	['PWRTRNM01', 'ELCM01', '1.11', 'ELCM02', '1', 'Power transmission Maluku Islands', '1'],
    	['PWRTRNN01', 'ELCN01', '1.11', 'ELCN02', '1', 'Power transmission Lesser Sunda Islands', '1'],
    	['PWRTRNP01', 'ELCP01', '1.11', 'ELCP02', '1', 'Power transmission Western New Guinea', '1'],
    	['PWRTRNL01', 'ELCL01', '1.11', 'ELCL02', '1', 'Power transmission Sulawesi', '1'],
    	['PWRTRNS01', 'ELCS01', '1.11', 'ELCS02', '1', 'Power transmission Sumatra', '1'],

        ['PWRTRNSJ1', 'ELCS02', '1.05', 'ELCJ01', '1', 'Power Transmission between Sumatra and Java.', '1'],
        ['PWRTRNSJ1', 'ELCJ02', '1.05', 'ELCS01', '1', '', '2'],
        ['PWRTRNJN1', 'ELCJ02', '1.05', 'ELCN01', '1', 'Power Transmission betweeen Java and Bali.', '1'],
        ['PWRTRNJN1', 'ELCN02', '1.05', 'ELCJ01', '1', '', '2'],

    	['UPSCRU001', 'CRU', '1.0', 'LPG', '0.0081', 'Crude oil refinery', '1'],
        ['UPSCRU001', '', '', 'GSL', '0.1694', 'Crude oil refinery', '1'],
    	['UPSCRU001', '', '', 'KER', '0.0694', '', '1'],
    	['UPSCRU001', '', '', 'DSL', '0.3221', '', '1'],
    	['UPSCRU001', '', '', 'HFO', '0.1429', '', '1'],
    	['UPSCRU001', '', '', 'OHC', '0.0816', '', '1'],

        # Structure of data is:  [Tech, InFuel, IAR, OutFuel, OAR, Name, Mode]
        # If the FUEL is '' that piece will not be created.

        # Name is used only the first time this technology shows up.  Fuels are created only if needed.

        # If multiple lines for the same technology, this technology will have multiple input and output activity ratios.

        # Note:  This section can also be used to add input or output fuels to various technologies (cooling water, for example)
    ]

    # Power Plants:
    PowerPlants = {
        'PWRCOAJ01':['Cilacap Adipala coal-fired 660 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS01':['Bangka Belitung 3 coal-fired 60 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ02':['Tanjung Jati-B II coal-fired 1320 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ03':['Tanjung Jati-B I coal-fired 1320 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ04':['Cirebon coal-fired 660 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ05':['Cilacap 600 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ06':['Labuan coal-fired 600 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS02':['Labuhan Angin coal-fired 230 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ07':['Lontar coal-fired 945 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS03':['Ombilin coal-fired 200 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ08':['Paiton (PLN) coal-fired 800 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ09':['Paiton 2300 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ10':['Pelabuhan Ratu coal-fired 1050 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ11':['Rembang coal-fired 630 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ12':['Pacitan coal-fired 630 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ13':['Indramayu coal-fired 990 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ14':['Suralaya coal-fired 3400 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ15':['Suralaya Baru coal-fired 625 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS04':['Bukit Asam coal-fired 260 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS05':['Tarahan coal-fired 200 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ16':['Java 4 coal-fired 2000 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ17':['Java 7 coal-fired 2000 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ18':['Central Java coal-fired (by the end of 2016) 2000 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ19':['Tanjung Awar-Awar coal-fired 700 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ20':['Madura coal-fired 200 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ21':['Bojonegara coal-fired 2220 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ22':['Tanjung Jati-A coal-fired 1320 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ23':['Nusa Penida coal-fired 200 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAJ24':['Anyer coal-fired 330 MW, Java-Bali power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS06':['Kuala Tanjung coal-fired 224 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS07':['Banjarsari coal-fired 200 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS08':['Banyuasin coal-fired 200 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS09':['Baturaja coal-fired 200 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS10':['Simpang Belimbing coal-fired 300 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS11':['Arahan coal-fired 2400 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAS12':['Central Bangko coal-fired 2480 MW, Sumatra power system.', 2.7, 0.0147, 0.014],
        'PWRCOAK01':['West Kalimantan 1 coal-fired 200 MW, Kalimantan power system.', 2.7, 0.0147, 0.014],
        'PWRCOAK02':['Tanjung coal-fired 110 MW, Kalimantan power system.', 2.7, 0.0147, 0.014],
        'PWRNGSJ01':['Bekasi 130 MW, West Java power system.', 1.76, 0.0124, 0.012],
        'PWRNGSS01':['Betara 70 MW, Sumatra power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ02':['Grati CCGT 764 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ03':['Gresik CCGT 2255 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ04':['Muara Tawar CCGT 920 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ05':['Muara Karang CCGT 1208 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRNGSS02':['Palembang Timur 150 MW, Sumatra power system.', 1.76, 0.0124, 0.012],
        'PWRNGSK01':['PLTG Senipah 92 MW, Kalimantan power system.', 1.76, 0.0124, 0.012],
        'PWRNGSK02':['PLTG/MG Kalbar Peaker 100 MW, Kalimantan power system.', 1.76, 0.0124, 0.012],
        'PWRNGSS03':['Sengkang 150 MW, Sumatra power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ06':['Tambak Lorok CCGT 1334 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ07':['Tanjung Priok CCGT 1430 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRDSLJ01':['Senayan Diesel 15 MW, Java-Bali power system.', 2.667, 0, 0],
        'PWRNGSJ08':['PLTU 400 MW 400 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRNGSJ09':['PLTGU 120 MW 120 MW, Java-Bali power system.', 1.76, 0.0124, 0.012],
        'PWRGEOJ01':['Kamojang geothermal 200 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOJ02':['Darajat geothermal 55 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOJ03':['Darajat geothermal 200 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOJ04':['Gunung Salak geothermal 180 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOJ05':['Gunung Salak geothermal 165 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOS01':['Ulubelu Geothermal Power Station 110 MW, Sumatra power system.', 1, 0.002, 0.0006],
        'PWRGEOJ06':['Wayang Windu geothermal 227 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOJ07':['Dieng geothermal 60 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRGEOL01':['Lahendong geothermal 80 MW, Sulawesi power system.', 1, 0.002, 0.0006],
        'PWRGEOS02':['Sibayak geothermal 11.3 MW, Sumatra power system.', 1, 0.002, 0.0006],
        'PWRGEOJ08':['Patuha geothermal 55 MW, Java-Bali power system.', 1, 0.002, 0.0006],
        'PWRHYDS01':['Agam hydro 10 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS02':['Maninjau hydro 68 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS03':['Singkarak hydro 175 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS04':['Koto Panjang hydro 114 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS05':['Test I hydro 16 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS06':['Musi hydro 210 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS07':['Besai hydro 90 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS08':['Batutegi hydro 28 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS09':['Lau Renun hydro 82 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS10':['Sipansihaporas hydro 50 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS11':['Asahan I hydro 180 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS12':['Asahan III hydro 174 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS13':['Sigura-gura hydro 286 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS14':['Tangga hydro 317 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS15':['Wampu hydro 45 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDS16':['Kerinci hydro 180 MW, Sumatra power system.', 1, 0, 0],
        'PWRHYDJ01':['Saguling hydro 701 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDJ02':['Cirata hydro 1008 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDJ03':['Jatiluhur hydro 186 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDJ04':['PB. Sudirman hydro 181 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDJ05':['Sutami hydro 105 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDJ06':['Wlingi hydro 54 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDL01':['Tonsea Lama hydro 14 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDL02':['Tanggari I & II hydro 36 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDL03':['Bakaru I & II hydro 191 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDL04':['Larona hydro 195 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDL05':['Balambano hydro 140 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDL06':['Karebbe hydro 132 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDL07':['Pamona 2 hydro 260 MW, Sulawesi power system.', 1, 0, 0],
        'PWRHYDK01':['Riam Kanan hydro 30 MW, Kalimantan power system.', 1, 0, 0],
        'PWRWNDJ01':['Possible wind power plant(s) in Java. Unlimited MW, Java-Bali power system.', 1, 0, 0],
        'PWRSOLJ01':['Possible solar power plant(s) in Java. Unlimited MW, Java-Bali power system.', 1, 0, 0],
        'PWRWNDL01':['Sidrap Wind Farm 75 MW, Sulawesi power system.', 1, 0, 0],
        'PWRDSLM01':['Diesal Power Plant Unlimited MW, Maluku Islands power system.', 2.667, 0, 0],
        'PWRDSLN01':['Diesal Power Plant Unlimited MW, Lesser Sunda Islands power system.', 2.667, 0, 0],
        'PWRDSLP01':['Diesal Power Plant Unlimited MW, Western New Guinea power system.', 2.667, 0, 0],
        'PWRDSLL01':['Diesal Power Plant Unlimited MW, Sulawesi power system.', 2.667, 0, 0],
        'PWRHYDJ07':['Hydro Expansion Potential MAX 5000 MW, Java-Bali power system.', 1, 0, 0],
        'PWRHYDS17':['Hydro Expansion Potential MAX 3000 MW, Sumatra power system.', 1, 0, 0],

    }

    Emissions = {
        'CO2NGS':	['Carbon dioxide emissions from natural gas.', '#000000'],
        'CO2PET':	['Carbon dioxide emissions from petroleum fuels.', '#cc9900'],
        'CO2COA':	['Carbon dioxide emissions from coal fuels.', '#00cc66']
    }

    Regions = {'REGION1': ['Region 1', '#000000']}


    NamingConvention = {
        'TRA': 'Transport',
        'OTH': 'Other',
        'BIO': 'Biomass',
        'COA': 'Coal',
        'CRU': 'Crude oil',
        'DSL': 'Diesel', 
        'ELC001': 'Electricity from power plants',
        'ELC002': 'Electricity from transmission',
        'ELCJ01': 'Electricity from power plants in Java region',
        'ELCJ02': 'Electricity from transmission in Java region',
        'ELCK01': 'Electricity from power plants in Kalimantan region',
        'ELCK02': 'Electricity from transmission in Kalimantan region',
        'ELCL01': 'Electricity from power plants in Sulawesi region',
        'ELCL02': 'Electricity from transmission in Sulawesi region',
        'ELCM01': 'Electricity from power plants in Maluku Islands region',
        'ELCM02': 'Electricity from transmission in Maluku Islands region',
        'ELCP01': 'Electricity from power plants in Western New Guinea region',
        'ELCP02': 'Electricity from transmission in Western New Guinea region',
        'ELCN01': 'Electricity from power plants in Lesser Sunda Islands region',
        'ELCN02': 'Electricity from transmission in Lesser Sunda Islands region',
        'ELCS01': 'Electricity from power plants in Sumatra region',
        'ELCS02': 'Electricity from transmission in Sumatra region',
        'GSL': 'Gasoline', 
        'HFO': 'Heavy fuel oil',
        'NGS': 'Natural gas',
        'KER': 'Kerosene',  
        'LPG': 'LPG', 
        'OHC': 'Other hydrocarbons',
        'GEO': 'Geothermal', 
        'HYD': 'Hydropower', 
        'SOL': 'Solar', 
        'WND': 'Wind',
        'CHC': 'Charcoal',
        'PCK': 'Petroleum coke',
        'JFL': 'Jet fuel',
    }

'''

if __name__ == "__main__":
    main()  