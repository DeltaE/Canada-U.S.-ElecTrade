"""Creates operational life and residual capacity data"""

import pandas as pd
import functions
from pathlib import Path


def main():
    """Creates operational life and residual capacity data.

    Creates operational life data for all technologies. Using these values,
    and commissioning dates for all existing power generation technologies,
    residual capacity for all Canadian regions is created. USA residual
    capacity data is taken from an existing dataset. All mining and
    renewable mining technologies have an operational life of 1 year.
    """

    #write Operational Life to a csv
    op_life_data, op_life, techs, tech_list_trade, df_trade = get_can_op_life()
    df_out_usa = get_usa_op_life()

    df_out = pd.DataFrame(op_life_data, columns=['REGION', 'TECHNOLOGY', 'VALUE'])
    df_out = df_out.append(df_out_usa)
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/OperationalLife.csv')
    df_out.to_csv(output_dir, index=False)

    #write Residual Capacity to a csv
    res_cap_data = get_can_res_cap(op_life, techs, tech_list_trade, df_trade)
    df_usa = get_usa_res_cap()

    df_out = pd.DataFrame(res_cap_data,
                         columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    df_out = df_out.append(df_usa)
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/ResidualCapacity.csv')
    df_out.to_csv(output_dir, index=False)


def get_can_op_life():
    """Creates canadian operational life data.

    Returns:
        op_life_data = Canadian Operational Life Data
        op_life = Dictionary from the tech, year values for use with residual capacity
        techs = List of technologies pertaining to Operational Life
        tech_list_trade = Trade names without duplicates
        df_trade = Raw Trade datafile
    """

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN']

    #read in raw operational life values
    df_op_life = pd.read_csv(
         Path(Path(__file__).resolve().parent,
        '../../resources/OperationalLifeTechnology.csv'))

    #remove P2G and FCL columns
    rows_drop = []
    for i in range(len(df_op_life)):
        tech = df_op_life['TECHNOLOGY'].iloc[i]
        if tech in ('P2G', 'FCL'):
            rows_drop.append(i)
    df_op_life = df_op_life.drop(rows_drop)
    df_op_life.reset_index()

    #Create a dictionary from the tech, year values for use with residual capacity
    techs = df_op_life['TECHNOLOGY'].tolist()
    op_life_years = df_op_life['YEARS'].tolist()
    op_life = {}
    for i in range(len(techs)):
        op_life[techs[i]] = op_life_years[i]

    #List to hold output operational life values
    #columns = region, technology, value
    op_life_data = []

    #save operational life to list
    for subregion in can_subregions:
        for tech, value in op_life.items():
            tech_name = 'PWR' + tech + 'CAN' + subregion + '01'
            op_life_data.append([continent, tech_name, value])

    # get trade tech names and save operational life values
    df_trade = pd.read_csv(Path(Path(__file__).resolve().parent,
        '../../resources/Trade.csv'))

    # get list of all the trade technologies
    tech_list_trade = df_trade['TECHNOLOGY'].tolist()
    tech_list_trade = list(set(tech_list_trade))  #remove duplicates

    # hardcode in operational life of 100 years
    for tech in tech_list_trade:
        op_life_data.append([continent, tech, 100])

    return op_life_data, op_life, techs, tech_list_trade, df_trade


def get_can_res_cap(op_life, techs, tech_list_trade, df_trade):
    """ Creates residual capacity data for all canadian technology data.

    Residual capacity values are calculated using comissioning dates of
    powerplants and applying an operational life value to find decomissioning
    year. There is no phase out period in residual capacity. Transmission
    capacity is never decomissioned.

    Args:
        op_life: Dictionary from tech and year values
        techs: List of technologies pertaining to Operational Life
        tech_list_trade: Trade names without duplicates
        df_trade: raw trade datafiel

    Returns:
        df_out: Canadian Residual Capacity Data
    """

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN']
    years = functions.get_years()

    #read in raw operational life values
    df_res_cap = pd.read_csv(Path(Path(__file__).resolve().parent,
        '../../resources/ResidualCapacitiesByProvince.csv'))

    #drop references column
    df_res_cap.drop(['Ref_1', 'Ref_2'], axis=1, inplace=True)

    # update retirment column based on comission date and operational life
    # if a user inputted number has been added, the retirement data is NOT updated
    comission_list = df_res_cap['COMISSION'].tolist()
    retirement_list = df_res_cap['RETIREMENT'].tolist()
    tech_list = df_res_cap['TECHNOLOGY'].tolist()

    for i in range(len(tech_list)):
        if retirement_list[i] == 0:
            retirement_list[i] = comission_list[i] + op_life[tech_list[i]]

    #Update retirement column
    df_res_cap['RETIREMENT'] = retirement_list

    # list to hold residual capacity values
    # columns = Region, Technology, Year, Value
    res_cap_data = []

    #populate data list
    for subregion, provinces in can_subregions.items():
        df_province = pd.DataFrame()  #Reset dataframe
        for province in provinces:
            df_temp = df_res_cap.loc[df_res_cap['PROVINCE'] == province]
            df_province = df_province.append(df_temp, ignore_index=True)
        for tech in techs:
            for year in years:
                df_filtered = df_province.loc[
                    (df_province['TECHNOLOGY'] == tech)
                    & (df_province['RETIREMENT'] >= year) &
                    (df_province['COMISSION'] <= year)]
                res_cap = df_filtered['CAPACITY (MW)'].sum()
                res_cap = res_cap / 1000  #MW -> GW
                res_cap = round(res_cap, 3)

                #create correct name
                tech_name = 'PWR' + tech + 'CAN' + subregion + '01'
                res_cap_data.append([continent, tech_name, year, res_cap])

    # Get trade residual capacity -- we are assuming no capacity in
    # transmission is being decommisioned
    for tech in tech_list_trade:
        df_res_cap_trade = df_trade.loc[(df_trade['TECHNOLOGY'] == tech)
                                  & (df_trade['MODE'] == 1)]
        df_res_cap_trade.reset_index()
        res_cap_trade = df_res_cap_trade['CAPACITY (GW)'].iloc[0]
        res_cap_trade = round(float(res_cap_trade), 3)
        for year in years:
            res_cap_data.append([continent, tech, year, res_cap_trade])

    return res_cap_data


def get_usa_op_life():
    """Creates operational life USA data.

    Returns:
        df_out: USA operational life data
    """
    # PURPOSE: Creates opertionalLife file from USA data
    # INPUT:   N/A
    # OUTPUT:  df_out = dataframe to be written to a csv

    continent = functions.get_from_yaml('continent')
    tech_map = functions.get_from_yaml('usa_tech_map')

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'), sheet_name='OperationalLife(r,t)')

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
        value = df['OPERATIONALLIFE'].iloc[i]
        out_data.append([continent, tech, value])

    #create and return datafram
    df_out = pd.DataFrame(out_data, columns=['REGION', 'TECHNOLOGY', 'VALUE'])
    return df_out


def get_usa_res_cap():
    """Creates USA residual capacity.

    USA data does not use operational life to gernerate decomissioning dates.
    Instead, it's directly read from the USA data file. Transmission
    capacity is never decomissioned.

    Returns:
        df_out: USA residual capacity dataframe
    """

    tech_map = functions.get_from_yaml('usa_tech_map')
    continent = functions.get_from_yaml('continent')

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'), sheet_name='ResidualCapacity(r,t,y)')

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
        value = df['RESIDUALCAPACITY'].iloc[i]
        value = round(value, 3)
        out_data.append([continent, tech, year, value])

    #create and return dataframe
    df_out = pd.DataFrame(out_data,
                         columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    return df_out


if __name__ == '__main__':
    main()
