"""Create input and output activity ratio"""

import pandas as pd
import functions


def main():
    """Creates otoole formatted input and output activity ratio files.

    All power generation and transmission technologies use the input activity
    ratio to define the efficiency (as IAR = 1/eff). Mining and renewable
    technologies have input activity ratios of 1. Output activity ratio for
    all technologies are 1
    """
    ############################################################
    ## EVERYTHING CURRENTLY MAPS TO MODE_OFOPERARION = 1
    ## WILL NEED TO UPDATE AFTER ADDING IN INTERNATIONAL TRADE
    ############################################################

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN'].keys()
    tech_to_fuel = functions.get_from_yaml('tech_to_fuel')
    rnw_fuels = functions.get_from_yaml('rnw_fuels')
    min_fuels = functions.get_from_yaml('mine_fuels')
    pwr_techs = functions.get_from_yaml('techs_master')
    years = functions.get_years()

    ###########################################
    # IAR and OAR of One
    ###########################################

    #columns = Region, Tech, Fuel, Mode, Year, Value
    master_iar = []
    master_oar = []

    # OAR Renweable Generations
    for year in years:
        for subregion in can_subregions:
            for fuel in rnw_fuels:
                tech_name = 'RNW' + fuel + 'CAN' + subregion
                fuel_out = fuel + 'CAN' + subregion
                master_oar.append([continent, tech_name, fuel_out, 1, year, 1])

    # OAR Domestic Mining
    for year in years:
        for fuel in min_fuels:
            tech_name = 'MIN' + fuel + 'CAN'
            fuel_out = fuel + 'CAN'
            master_oar.append([continent, tech_name, fuel_out, 1, year, 1])

    # IAR and OAR International Mining
    for year in years:
        for fuel in min_fuels:
            tech_name = 'MIN' + fuel + 'INT'
            fuel_in = fuel
            fuel_out = fuel + 'INT'
            master_iar.append([continent, tech_name, fuel_in, 1, year, 1])
            master_oar.append([continent, tech_name, fuel_out, 1, year, 1])

    # IAR and OAR for PWRTRN technologies
    for year in years:
        for subregion in can_subregions:
            tech_name = 'PWR' + 'TRN' + 'CAN' + subregion
            fuel_in = 'ELC' + 'CAN' + subregion + '01'
            fuel_out = 'ELC' + 'CAN' + subregion + '02'
            master_iar.append([continent, tech_name, fuel_in, 1, year, 1])
            master_oar.append([continent, tech_name, fuel_out, 1, year, 1])

    # IAR and OAR for TRN technologies
    df = pd.read_csv('../dataSources/Trade.csv')
    for year in years:
        for i in range(len(df)):
            tech_name = df.iloc[i]['TECHNOLOGY']
            in_fuel = df.iloc[i]['INFUEL']
            out_fuel = df.iloc[i]['OUTFUEL']
            iar = df.iloc[i]['IAR']
            oar = df.iloc[i]['OAR']
            mode = df.iloc[i]['MODE']
            master_iar.append([continent, tech_name, in_fuel, mode, year, iar])
            master_oar.append([continent, tech_name, out_fuel, mode, year, oar])

    # IAR and OAR for RNW PWR technologies
    df_iar = pd.read_csv('../dataSources/InputActivityRatioByTechnology.csv',
                         index_col=0)
    df_oar = pd.read_csv('../dataSources/OutputActivityRatioByTechnology.csv',
                         index_col=0)
    for year in years:
        for subregion in can_subregions:
            for fuel in pwr_techs:
                tech_name = 'PWR' + fuel + 'CAN' + subregion + '01'
                iar = df_iar.loc[year, fuel]
                oar = df_oar.loc[year, fuel]
                fuel_name = tech_to_fuel[fuel]

                # if has international imports
                if fuel_name in min_fuels:
                    in_fuel_mode_one = fuel_name + 'CAN'
                    in_fuel_mode_two = fuel_name + 'INT'
                    out_fuel = 'ELC' + 'CAN' + subregion + '01'
                    master_iar.append(
                        [continent, tech_name, in_fuel_mode_one, 1, year, iar])
                    master_iar.append(
                        [continent, tech_name, in_fuel_mode_two, 2, year, iar])
                    master_oar.append(
                        [continent, tech_name, out_fuel, 1, year, oar])
                    master_oar.append(
                        [continent, tech_name, out_fuel, 2, year, oar])

                # edge case of storage. This is super hacked together...
                elif fuel == 'P2G' or fuel == 'FCL':
                    # P2G will only have input activity ratio
                    if fuel == 'P2G':
                        in_fuel = 'ELC' + 'CAN' + subregion + '02'
                        out_fuel = 'HY2' + 'CAN' + subregion + '01'
                        master_iar.append(
                            [continent, tech_name, in_fuel, 1, year, iar])
                        master_oar.append(
                            [continent, tech_name, out_fuel, 1, year, 0])
                    # P2G will only have output activity ratio
                    elif fuel == 'FCL':
                        in_fuel = 'HY2' + 'CAN' + subregion + '01'
                        out_fuel = 'ELC' + 'CAN' + subregion + '02'
                        master_iar.append(
                            [continent, tech_name, in_fuel, 1, year, 0])
                        master_oar.append(
                            [continent, tech_name, out_fuel, 1, year, oar])
                # Renewables
                else:
                    in_fuel = fuel_name + 'CAN' + subregion
                    out_fuel = 'ELC' + 'CAN' + subregion + '01'
                    master_iar.append(
                        [continent, tech_name, in_fuel, 1, year, iar])
                    master_oar.append(
                        [continent, tech_name, out_fuel, 1, year, oar])

    #write IAR and OAR to files
    df_iar_out = pd.DataFrame(master_iar,
                              columns=[
                                  'REGION', 'TECHNOLOGY', 'FUEL',
                                  'MODE_OF_OPERATION', 'YEAR', 'VALUE'])
    df_iar_usa = get_usa_iar()
    df_iar_out = df_iar_out.append(df_iar_usa)
    df_iar_out.to_csv('../src/data/InputActivityRatio.csv', index=False)

    df_oar_out = pd.DataFrame(master_oar,
                              columns=[
                                  'REGION', 'TECHNOLOGY', 'FUEL',
                                  'MODE_OF_OPERATION', 'YEAR', 'VALUE'])
    df_oar_usa = get_usa_oar()
    df_oar_out = df_oar_out.append(df_oar_usa)
    df_oar_out.to_csv('../src/data/OutputActivityRatio.csv', index=False)


def get_usa_oar():
    """Creates output activity ratio data for USA.

    Returns:
        df_out = dataframe with usa output activity ratio values
    """

    # PARAMETERS

    tech_map = functions.get_from_yaml('usa_tech_map')
    usa_subregions = functions.get_from_yaml('regions_dict')['USA']
    continent = functions.get_from_yaml('continent')
    int_fuels = functions.get_from_yaml('mine_fuels')
    rnw_fuels = functions.get_from_yaml('rnw_fuels')
    years = functions.get_years()

    #holds output data
    out_data = []

    #renewables
    for year in years:
        for rnw_fuel in rnw_fuels:
            for subregion in usa_subregions:
                tech_name = 'RNW' + rnw_fuel + 'USA' + subregion
                fuel = rnw_fuel + 'USA' + subregion
                out_data.append([continent, tech_name, fuel, 1, year, 1])

    #mining USA
    for year in years:
        for int_fuel in int_fuels:
            tech_name = 'MIN' + int_fuel + 'USA'
            fuel = int_fuel + 'USA'
            out_data.append([continent, tech_name, fuel, 1, year, 1])

    # OAR for PWRTRN technologies
    for subregion in usa_subregions:
        for year in years:
            tech_name = 'PWR' + 'TRN' + 'USA' + subregion
            fuel = 'ELC' + 'USA' + subregion + '02'
            out_data.append([continent, tech_name, fuel, 1, year, 1])

    # OAR for PWR technologies
    for year in years:
        for subregion in usa_subregions:
            for tech in tech_map:
                tech_name = 'PWR' + tech_map[tech] + 'USA' + subregion + '01'
                fuel = 'ELC' + 'USA' + subregion + '01'
                out_data.append([continent, tech_name, fuel, 1, year, 1])
                if tech_map[tech] in int_fuels:
                    out_data.append([continent, tech_name, fuel, 2, year, 1])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'FUEL',
                              'MODE_OF_OPERATION', 'YEAR', 'VALUE'])
    return df_out


def get_usa_iar():
    """Creates input activity ratio data for USA

    Returns:
        df_out = dataframe with usa input activity ratio values
    """

    tech_map = functions.get_from_yaml('usa_tech_map')
    usa_subregions = functions.get_from_yaml('regions_dict')['USA']
    input_fuel_map = functions.get_from_yaml('tech_to_fuel')
    continent = functions.get_from_yaml('continent')
    int_fuels = functions.get_from_yaml('mine_fuels')
    years = functions.get_years()

    df = pd.read_excel('../dataSources/USA_Data.xlsx',
                       sheet_name='InputActivityRatio(r,t,f,m,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #Initialize filtered dataframe
    columns = list(df)
    df_filtered = pd.DataFrame(columns=columns)

    #get rid of all techs we are not using
    for tech in tech_map:
        df_temp = df.loc[df['TECHNOLOGY'] == tech]
        df_filtered = df_filtered.append(df_temp)

    df = df_filtered
    df.reset_index()

    #holds output data
    out_data = []

    #map data
    for i in range(len(df)):
        tech_mapped = tech_map[df['TECHNOLOGY'].iloc[i]]
        tech = 'PWR' + tech_mapped + 'USA' + df['REGION'].iloc[i] + '01'
        year = df['YEAR'].iloc[i]
        value = df['INPUTACTIVITYRATIO'].iloc[i]
        value = round(value, 3)
        fuel_mapped = input_fuel_map[tech_mapped]

        #check if tech will operate on two modes of operation
        if fuel_mapped in int_fuels:
            fuel = fuel_mapped + 'USA'
            out_data.append([continent, tech, fuel, 1, year, value])
            fuel = fuel_mapped + 'INT'
            out_data.append([continent, tech, fuel, 2, year, value])
        else:
            fuel = fuel_mapped + 'USA' + df['REGION'].iloc[i]
            out_data.append([continent, tech, fuel, 1, year, value])

    # IAR for PWRTRN technologies
    for subregion in usa_subregions:
        for year in years:
            tech_name = 'PWR' + 'TRN' + 'USA' + subregion
            fuel_in = 'ELC' + 'USA' + subregion + '01'
            out_data.append([continent, tech_name, fuel_in, 1, year, 1])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'FUEL',
                              'MODE_OF_OPERATION', 'YEAR', 'VALUE'])
    return df_out


if __name__ == '__main__':
    main()
