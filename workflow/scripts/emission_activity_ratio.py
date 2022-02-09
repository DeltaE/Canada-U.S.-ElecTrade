"""Creates emission activity ratio data."""

import pandas as pd
import functions
from pathlib import Path


def main():
    """Creates emission activity ratio data for both countries.

    Generates Canadian emission activity ratios from raw collected datasheet.
    Generates USA emission activity ratio from exisiting USA dataset.
    EVERYTHING MAPS TO MODE_OFOPERARION = 1 AND IS CO2 EQUIVALENT VALUES
    """

    # GET DATA

    data_out = get_can_emission_activity_ratio()
    df_usa = get_usa_emission_activity_ratio()

    # SAVE DATA

    df_out = pd.DataFrame(data_out,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'EMISSION',
                              'MODE_OF_OPERATION', 'YEAR', 'VALUE'
                          ])
    df_out = df_out.append(df_usa)
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/EmissionActivityRatio.csv')
    df_out.to_csv(output_dir, index=False)


def get_can_emission_activity_ratio():
    """Generates Emission Activity Ratio for Canada.

    Returns:
        dataOut: Canadian Emission Activity Ratio data
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN'].keys()
    years = functions.get_years()

    #read in raw emission activity values
    df_raw = pd.read_csv(Path(Path(__file__).resolve().parent,
        '../../resources/EmissionActivityRatioByTechnology.csv'), index_col=0)

    #list to hold all output values
    data_out = []

    #get list of technologies to print over
    tech_list = list(df_raw)

    #Techs that operate on two modes of operation
    mode_two_techs = ['CCG', 'CTG', 'COA', 'COC', 'URN']

    #print all values
    for year in years:
        for subregion in can_subregions:
            for tech in tech_list:
                activity_ratio = df_raw.loc[year, tech]
                activity_ratio = round(activity_ratio, 3)
                tech_name = 'PWR' + tech + 'CAN' + subregion + '01'
                data_out.append(
                    [continent, tech_name, 'CO2', 1, year, activity_ratio])
                if tech in mode_two_techs:
                    data_out.append(
                        [continent, tech_name, 'CO2', 2, year, activity_ratio])

    return data_out


def get_usa_emission_activity_ratio():
    """Generates Emission Activity Ratio for USA.

    Returns:
        df_out: USA Emission Activity Ratio data
    """

    tech_map = functions.get_from_yaml('usa_tech_map')
    input_fuel_map = functions.get_from_yaml('tech_to_fuel')
    continent = functions.get_from_yaml('continent')
    int_fuel = functions.get_from_yaml('mine_fuels')  # International trade
    years = functions.get_years()

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'),
        sheet_name='EmisionActivityRatio(r,t,e,m,y)')

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
    for year in years:
        for i in range(len(df)):
            tech_mapped = tech_map[df['TECHNOLOGY'].iloc[i]]
            tech = 'PWR' + tech_mapped + 'USA' + df['REGION'].iloc[i] + '01'
            emission = df['EMISSION'].iloc[i]
            mode = 1
            value = df['EMISSIONACTIVITYRATIO'].iloc[i]
            value = round(value, 3)
            out_data.append([continent, tech, emission, mode, year, value])
            #checks if need to write value for mode 2
            if input_fuel_map[tech_mapped] in int_fuel:
                mode = 2
                out_data.append([continent, tech, emission, mode, year, value])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'EMISSION',
                              'MODE_OF_OPERATION', 'YEAR', 'VALUE'
                          ])
    return df_out


if __name__ == '__main__':
    main()
