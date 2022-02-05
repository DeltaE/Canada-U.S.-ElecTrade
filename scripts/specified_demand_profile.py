"""Creates specified demand profile data."""

import pandas as pd
import functions


def main():
    """Creates formatted specified demand profile data.

    Creates an otoole formatted CSV holding the specified demand profile for
    the model. Accounts for time zones and daylight saving time. Data for one
    year is copied over for all years.

    """

    # GET DATA

    df_can = get_can_specified_demand_profile()
    df_usa = get_usa_specified_demand_profile()

    # WRITE DATA

    df = pd.DataFrame(df_can,
                      columns=['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    df = df.append(df_usa)
    df.to_csv('../src/data/SpecifiedDemandProfile.csv', index=False)


def get_can_specified_demand_profile():
    """ Gets Canadian specified demand profile.

    Returns:
        load: List of lists describing load profile data for Canada.
    """

    # PARAMETERS

    seasons = functions.get_from_yaml(
        'seasons')  # Dictionary holds month to season Mapping
    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')[
        'CAN']  # Canadian subregions
    years = functions.get_years()

    # CALCULATIONS

    #generate master load dataframe
    df_load = functions.get_load_values()

    #Master list to output
    #Region, fuel, timeslice, year, value
    load = []

    # Looping years here isnt super efficient. But it isnt a very long script
    # and it make the output csv easy to read
    for year in years:

        #filter dataframe by subregion
        for subregion, provinces in can_subregions.items():
            df_subregion = pd.DataFrame()  #reset df
            for province in provinces:
                df_province = df_load.loc[df_load['PROVINCE'] == province]
                df_subregion = df_subregion.append(df_province,
                                                   ignore_index=True)

            #Get total load for year so we can normalize
            total_load = df_subregion['VALUE'].sum()

            #filter dataframe by season
            for season, months in seasons.items():
                df_season = pd.DataFrame()  #reset df
                for month in months:
                    df_month = df_subregion.loc[df_subregion['MONTH'] == month]
                    df_season = df_season.append(df_month, ignore_index=True)

                #filter dataframe by timeslice
                for hour in range(1, 25):
                    ts = season + str(hour)
                    df_filter = df_season.loc[df_season['HOUR'] == hour]
                    profile_value = df_filter['VALUE'].sum() / total_load
                    profile_value = round(profile_value, 3)
                    #pd.set_option('display.max_rows', df_filter.shape[0]+1)
                    #print(df_filter)

                    #Assign fuel name
                    fuel_name = 'ELC' + 'CAN' + subregion + '02'

                    #save profile value
                    load.append(
                        [continent, fuel_name, ts, year, profile_value])

    return load


def get_usa_specified_demand_profile():
    """ Gets USA specified demand profile.

    Returns:
        df_out: dataframe describing load profile data for USA.
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    df = pd.read_excel('../dataSources/USA_Data.xlsx',
                       sheet_name='SpecifiedDemandProfile(r,f,l,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    # MAPS DATA

    #holds output data
    out_data = []
    for i in range(len(df)):
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        ts = df['TIMESLICE'].iloc[i]
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        value = round(value, 3)
        out_data.append([continent, fuel, ts, year, value])

    #create and return datafram
    df_out = pd.DataFrame(
        out_data, columns=['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE'])
    return df_out


if __name__ == '__main__':
    main()
