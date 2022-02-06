"""Functions and constants common between multiple files"""

import datetime
import pandas as pd
import yaml
from pathlib import Path


# CONSTANTS

# Province to Time Zone Mapping
_PROVINCIAL_TIME_ZONES = {
    'BC': 0,
    'AB': 1,
    'SK': 2,
    'MB': 2,
    'ON': 3,
    'QC': 3,
    'NB': 4,
    'NL': 4,
    'NS': 4,
    'PE': 4
}

# SHARED FUNCTIONS

def get_from_yaml(name):
    """Returns a value from the config.yaml file

    The user can modify any values in the config.yaml file for scenario
    analysis

    Args:
        name: name of the value being retrieved

    Returns:
        parsedYaml: the value from the yaml file
    """

    p = Path(Path(__file__).resolve().parent, '../../config/config.yaml')
    with open(p, encoding='utf-8') as yaml_file:
        yaml_parsed = yaml.load(yaml_file, Loader=yaml.FullLoader).get(name)
    return yaml_parsed


def get_years():
    """Gets model horizon from config.yaml file

    Returns:
        years: list of years over the model horizon
    """

    start_year = get_from_yaml('start_year')
    end_year = get_from_yaml('end_year')

    return range(start_year, end_year + 1)


def get_load_values():
    """Parses hourly load values for Canadian provinces

    Returns:
        df_out: dataframe with load vales for each province
            columns = Province, Month, Day, Hour, Load Value
    """

    #Read in all provinces
    source_file = Path(Path(__file__).resolve().parent,
        '../../resources/ProvincialHourlyLoads.xlsx')
    sheets = pd.read_excel(source_file, sheet_name=None)

    #Will store output information with the columns...
    #Province, month, hour, load [MW]
    data = []

    #Loop over sheets and store in a master list
    for province, sheet in sheets.items():
        date_list = sheet['Date'].tolist()
        hour_list = sheet['HOUR (LOCAL)'].tolist()
        load_list = sheet['LOAD [MW]'].tolist()

        #loop over list and break out month, day, hour from date
        for i in range(len(date_list)):
            date_full = date_list[i]
            date = datetime.datetime.strptime(date_full, '%Y-%m-%d')

            # Shift time values to match BC time (ie. Shift 3pm Alberta time
            # back one hour, so all timeslices represent the asme time)
            hour_adjusted = int(
                hour_list[i]) - _PROVINCIAL_TIME_ZONES[province]
            if hour_adjusted < 1:
                hour_adjusted = hour_adjusted + 24

            #Save data
            data.append(
                [province, date.month, date.day, hour_adjusted, load_list[i]])

    #process daylight savings time values
    data = daylight_savings(data)

    #dataframe to output
    df_out = pd.DataFrame(
        data, columns=['PROVINCE', 'MONTH', 'DAY', 'HOUR', 'VALUE'])
    return df_out


def daylight_savings(in_data):
    """Processess a dataset to accout for daylight savings time

    Assumes daylight savings time is not in the first of last day of the list.
    The following logic is used to deal with the dst reported values
        1. If the DST gives a load of zero -> the load at the same time in the
           previous day is used.
        2. If the DST lists a double load -> the same load as the previous hour
           is used.

    Args:
        in_data: list with the columns: Province, Month, Day, Hour, Load Value

    Returns:
        out_data: list with the columns: Province, Month, Day, Hour, Load Value
    """

    # Split this into two for loop for user clarity when reading output file.
    # The faster option willbe to just append the added values to the end of
    # the list in the first list

    #keep track of what rows to remove data for
    rows_to_remove = []
    rows_to_add = []

    for i in range(len(in_data) - 1):
        #check if one hour is the same as the next
        if in_data[i][3] == in_data[i + 1][3]:
            #Check that regions are the same
            if in_data[i][0] == in_data[i + 1][0]:
                average = (in_data[i][4] + in_data[i + 1][4]) / 2
                in_data[i + 1][4] = average
                rows_to_remove.append(i)
                # print(f'hour averaged for {in_data[i][0]} on month'
                # f'{in_data[i][1]}, day {in_data[i][2]}, hour {in_data[i][3]}')

    #Remove the rows in reverse order so  counting starts from start of the list
    for i in reversed(rows_to_remove):
        in_data.pop(i)

    #check if hour is missing a load
    for i in range(len(in_data) - 1):
        #first condition if data marks the load as zero
        if in_data[i][4] < 1:
            in_data[i][4] = in_data[i - 1][4]
            # print(f'hour modified for {in_data[i][0]} on month'
            # f'{in_data[i][1]}, day {in_data[i][2]}, hour {in_data[i][3]}')
        #second and third conditions for if data just skips the time step
        elif (int(in_data[i + 1][3]) - int(in_data[i][3]) == 2) or (
            int(in_data[i][3]) - int(in_data[i + 1][3]) == 22):
            rows_to_add.append(i)
            # print(f'hour added for {in_data[i][0]} on month '
            # f'{in_data[i][1]}, day {in_data[i][2]}, hour {in_data[i][3]}')

    #Add the rows in reverse order to count from the start of the list
    for i in reversed(rows_to_add):
        row_after = in_data[i + 1]
        new_hour = row_after[3] - 1
        new_row = [
            row_after[0], row_after[1], row_after[2], new_hour, row_after[4]]
        in_data.insert(i, new_row)

    return in_data


def get_pwr_techs(region, techs):
    """Creates PWR naming technologies.

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)
        tech: List of the technologies to print over

    Returns:
        out_list: List of all the PWR technologies
    """

    # list to hold technologies
    out_list = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        for tech in techs:
            tech_name = 'PWR' + tech + region[0] + subregion + '01'
            out_list.append(tech_name)

    # Return list of pwr Technologes
    return out_list


def get_pwrtrn_techs(region):
    """Creates PWRTRN naming technologies.

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)

    Returns:
        out_list: List of all the PWRTRN technologies
    """

    # list to hold technologies
    out_list = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        tech_name = 'PWR' + 'TRN' + region[0] + subregion
        out_list.append(tech_name)

    # Return list of pwr Technologes
    return out_list


def get_min_techs(region, techs):
    """Creates MIN naming technologies.

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)
        tech: List of the technologies to print over

    Returns:
        out_list: List of all the MIN technologies
    """

    # list to hold technologies
    out_list = []

    # Loop to create all regionalized technology names
    for tech in techs:
        tech_name = 'MIN' + tech + region[0]
        out_list.append(tech_name)

    # Return list of min Technologes
    return out_list


def get_rnw_techs(region, techs):
    """Creates RNW naming technologies.

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)
        tech: List of the technologies to print over

    Returns:
        out_list: List of all the RNW technologies
    """

    # list to hold technologies
    out_list = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        for tech in techs:
            tech_name = 'RNW' + tech + region[0] + subregion
            out_list.append(tech_name)

    # Return list of rnw Technologes
    return out_list


def get_trn_techs(csv_name):
    """Creates TRN naming technologies.

    Args:
        csv_path: Transmission data csv name in resources folder

    Returns:
        out_list: List of all the TRN technologies
    """
    path = Path(Path(__file__).resolve().parent, '../../resources', csv_name)
    df = pd.read_csv(path)
    out_list = df['TECHNOLOGY'].tolist()
    out_list = list(set(out_list))  # remove duplicates

    return out_list


def get_rnw_fuels(region, techs):
    """Creates fuels for RNW technologies.

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)
        tech: List of the RNW technologies to print over

    Returns:
        out_list: List of all fuels for RNW technologies
    """

    # list to hold technologies
    out_list = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        for tech in techs:
            fuel_name = tech + region[0] + subregion
            out_list.append(fuel_name)

    # Return list of rnw fuels
    return out_list


def get_min_fuels(region, techs):
    """Creates fuels for MIN technologies.

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)
        tech: List of the MIN technologies to print over

    Returns:
        out_list: List of all fuels for MIN technologies
    """

    # list to hold technologies
    out_list = []

    # Loop to create all technology names based on region
    for tech in techs:
        fuel_name = tech + region[0]
        out_list.append(fuel_name)

    # Return list of min TFuels
    return out_list


def get_elc_fuels(region):
    """Creates electricity fuel names:

    Args:
        region: Tuple holding country as the key and subregion as the values
                in a dictionary (CAN, {WS:[...], MW:[]...},)

    Returns:
        out_list: list of all ELC fuels
    """

    # list to hold technologies
    out_list = []

    # Loop to create all technology names
    for subregion in region[1].keys():
        elc_one = 'ELC' + region[0] + subregion + '01'
        elc_two = 'ELC' + region[0] + subregion + '02'
        out_list.extend([elc_one, elc_two])

    # Return list of electricty fuels
    return out_list


def create_fuel_df(subregions, rnw_fuels, mine_fuels):
    """Creates all national and international fuels

    Args:
        subregions = Dictionary holding Country and regions
            ({CAN:{WS:[...], ...}, USA:[NY:[...],...]})
        rnw_fuels = List of the fuels to print over for get_rnw_fuels
        mine_fuels = List of the fuels to print over for get_min_fuels

    Returns:
        df_out: fuel set dataframe
    """

    output_fuels = []
    for region in subregions.items():
        # Renewable fuels
        rnw_fuel_list = get_rnw_fuels(region, rnw_fuels)

        # Mining fuels
        min_fuel_list = get_min_fuels(region, mine_fuels)

        #ELC fuels
        elc_fuel_list = get_elc_fuels(region)

        #Hydrogen Fuels
        #hy2FuelList = getHY2fuels(countries)

        #Append lists together
        output_fuels += rnw_fuel_list
        output_fuels += min_fuel_list
        output_fuels += elc_fuel_list
        #output_fuels.append(hy2FuelList)

    # Loop to create all technology names for international import/export
    for fuel in mine_fuels:
        fuel_name = fuel + 'INT'
        output_fuels.append(fuel_name)
    for fuel in mine_fuels:
        output_fuels.append(fuel)

    df_out = pd.DataFrame(output_fuels, columns=['VALUE'])

    return df_out


def create_tech_df(subregions, techs_master, mine_fuels, rnw_fuels, trn_techs_csv_name):
    """Describes all technologies in dataframe format

    Args:
        subregions = Dictionary holding Country and regions
            ({CAN:{WS:[...], ...} USA:[NY:[...],...]})
        techs_master = List of the technologies to print over for get_pwr_techs
        mine_fuels = List of the fuels to print over for get_min_fuels
        rnw_fuels = List of the fuels to print over for get_rnw_fuels
        trn_techs_csv_name = Name of csv in resources folder

    Returns:
        df_out = tech set dataframe
    """

    # get power generator technology list
    output_techs = []
    for region in subregions.items():

        pwr_list = get_pwr_techs(region, techs_master)

        # get grid distribution technology list (PWRTRN<Reg><SubReg>)
        pwr_trn_list = get_pwrtrn_techs(region)

        # get Mining techs list
        min_list = get_min_techs(region, mine_fuels)

        # get Renewables fuels list
        rnw_list = get_rnw_techs(region, rnw_fuels)

        #Append lists together
        output_techs += pwr_list
        output_techs += pwr_trn_list
        output_techs += min_list
        output_techs += rnw_list

    # get trade technology list
    trn_list = get_trn_techs(trn_techs_csv_name)
    output_techs += trn_list

    #Generate international trade
    for tech in mine_fuels:
        tech_name = 'MIN' + tech + 'INT'
        output_techs.append(tech_name)

    df_out = pd.DataFrame(output_techs, columns=['VALUE'])

    return df_out


def create_tech_list(techs_master, rnw_techs, mine_techs, sto_techs):
    """Describes all technologies in list format

    Args:
        techs_master = List of the technologies to print over for power techs
        rnw_techs = List of the technologies to print over for renewable techs
        mine_techs = List of the technologies to print over for mining techs
        sto_techs = List of the technologies to print over for storage techs

    Returns:
        data: list of all technologies
    """

    # get power generator technology list
    data = []

    for i in range(len(techs_master)):
        data.append(['PWR', techs_master[i]])

    for i in range(len(rnw_techs)):
        data.append(['RNW', rnw_techs[i]])

    for i in range(len(mine_techs)):
        data.append(['MIN', mine_techs[i]])

    for i in range(len(sto_techs)):
        data.append(['STO', sto_techs[i]])

    return data


def get_usa_capacity_availability_factor(is_capacity):
    """Creates CapacityFactor or AvailabilityFactor file from USA data.

    Args:
        is_capacity = Boolean indicating Capacity Factor should be returned
            when true. Availability factor otherwise

    Returns:
        df_out: dataframe of USA capacity facotor or availability factor data
    """

    tech_map = get_from_yaml('usa_tech_map')
    continent = get_from_yaml('continent')
    years = get_years()

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'), sheet_name='CapacityFactor(r,t,l,y)')

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
    out_data_cf = []  # Capacity Factor
    out_data_af = []  # Availability Factor

    #map data
    for year in years:
        for i in range(len(df)):
            tech_mapped = tech_map[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + tech_mapped + 'USA' + df['REGION'].iloc[i] + '01'
            ts = df['TIMESLICE'].iloc[i]
            value = df['CAPACITYFACTOR'].iloc[i]
            value = round(value, 3)
            if tech_mapped == 'HYD':
                out_data_af.append([continent, tech, ts, year, value])
            else:
                out_data_cf.append([continent, tech, ts, year, value])

    #create and return dataframe for CAPACITY FACTOR
    df_out_cf = pd.DataFrame(
        out_data_cf,
        columns=['REGION', 'TECHNOLOGY', 'TIMESLICE', 'YEAR', 'VALUE'])

    if is_capacity:  # Return Capacity Factor
        return df_out_cf
    else:  # Return Availability Factor
        df_af = pd.DataFrame(
            out_data_af,
            columns=['REGION', 'TECHNOLOGY', 'TIMESLICE', 'YEAR', 'VALUE'])
        af_techs = df_af['TECHNOLOGY'].to_list()
        af_techs = list(set(af_techs))

        out_data_af = []
        for tech in af_techs:
            df_temp = df_af.loc[df_af['TECHNOLOGY'] == tech]
            for year in years:
                df_year = df_temp.loc[df_temp['YEAR'] == year]
                af = df_year['VALUE'].mean()
                af = round(af, 3)
                out_data_af.append([continent, tech, year, af])

        # return dataframe for CAPACITY FACTOR
        df_out_af = pd.DataFrame(
            out_data_af, columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
        return df_out_af
