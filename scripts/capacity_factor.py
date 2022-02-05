"""Creates capacity factor data."""

import pandas as pd
import datetime
import functions
import sys


# MODULE CONSTANTS

#Dictionary to hold land area for averaging (thousand km2)
_PROVINCIAL_LAND_AREAS = {
    'BC':945,
    'AB':661,
    'SK':651,
    'MB':647,
    'ON':1076,
    'QC':1542,
    'NB':73,
    'NL':405,
    'NS':55,
    'PE':6}

def main():
    """Generates capacity factor data for all technologies.

    All United States capacity factors are copied over from the existing
    dataset. Canadian capacity factors are generated from historical weather
    data or published datasets for thermal stations. Capacity factors for the
    first year are copied over for all years.
    """

    # PARAMETERS

    seasons = functions.get_from_yaml('seasons')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN']
    years = functions.get_years()

    # CALCULATIONS

    df_wind = variable_cap_factor('WND', can_subregions, seasons, years)
    df_pv = variable_cap_factor('SPV', can_subregions, seasons, years)
    df_fossil = read_nrel(can_subregions, seasons, years)
    df_usa = functions.get_usa_capacity_availability_factor(True)

    # WRITING FILES

    #output dataframe
    df = pd.DataFrame(
        columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    df = df.append(df_wind)
    df = df.append(df_pv)
    df = df.append(df_fossil)
    df = df.append(df_usa)

    df.to_csv('../src/data/CapacityFactor.csv', index=False)

def variable_cap_factor(tech, subregions, seasons, years):
    """Generates variable renewable capacity factor data for Canada.

    Takes a folder of CSVs created by renewable Ninja and formats a dataframe
    to hold all capacity factor values

    Args:
        tech: 'WIND' or 'PV' coresponding to a folder of CSVs containing raw
            renewable.ninja data (<TECH>_<PROVINCE>.csv)
        subregions: Dictionary for subregion to province mapping
        seasons: Dictionary for season to month mapping
        years: List of years to populate data for

    Returns:
        df_out: otoole formatted dataframe with capacity factor values
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    hour_list = range(1,25)

    #Holds data to be written to a csv
    data = []

    #get formatted data for each region and append to output dataframe
    for subregion in subregions:
        df_province = pd.DataFrame(
            columns = ['PROVINCE','SEASON','HOUR','VALUE'])
        for province in subregions[subregion]:
            csv_name = tech + '_' + province + '.csv'
            df_temp = read_renewable_ninja_data(csv_name, province)
            df_temp = monthly_average_cf(df_temp)
            df_temp = seasonal_average_cf(df_temp, seasons)
            df_province = df_province.append(df_temp, ignore_index = True)

        #Find total land area of region for calcaulting weighted averages
        subregion_area = 0
        for province in subregions[subregion]:
            subregion_area = subregion_area + _PROVINCIAL_LAND_AREAS[province]

        #Filter dataframe for each season and timeslice
        for year in years:
            print (f'{subregion} {tech} {year}')
            for season in seasons:
                #for month in seasons[season]:
                for hour in hour_list:
                    df_filter = df_province.loc[
                        (df_province['SEASON'] == season) &
                        (df_province['HOUR'] == hour)]
                    provinces = list(df_filter['PROVINCE'])
                    cf_list = list(df_filter['VALUE'])

                    #Find average weighted average capacity factor
                    cf = 0
                    for i in range(len(provinces)):
                        weighting_factor = _PROVINCIAL_LAND_AREAS[
                            provinces[i]]/subregion_area
                        cf = cf + cf_list[i] * weighting_factor

                    #round cf
                    cf = round(cf,3)

                    #create timeslice value
                    ts = season + str(hour)

                    #create tech name
                    tech_name = 'PWR' + tech + 'CAN' + subregion + '01'

                    #Append data to output data list
                    data.append([continent, tech_name, ts, year, cf])

    #output dataframe
    df_out = pd.DataFrame(data,
        columns=['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    return df_out

def read_renewable_ninja_data(csv_name, province):
    """ Parse raw renewable.ninja file.

    Reads in a raw renewable.ninja file, removes everything except local time
    and CF value. Parses the date column to seperate month, day, and hour
    columns

    Args:
        csvName: Name of csv file to read in WITH csv extension (.csv)
        province: Name of province to parse data for, following standard two
            letter province abbreviations.

    Returns:
        df_out: Dataframe with the columns: Province, Month, Day, Hour, CF Value
    """

    # Read in CSV file
    source_file = '../dataSources/CapacityFactor/' + csv_name
    df = pd.read_csv(source_file, header=None, skiprows=[0,1,2,3])

    # Drop everything except columns 2,3 (Local time and capacity factor)
    df = df[[df.columns[1],df.columns[2]]]

    #add headers and parse to lists
    df.columns = ['date','value']
    date_list = df['date'].tolist()
    cf_list = df['value'].tolist()

    #List to hold all data in to be written to a dataframe
    data = []

    #loop over list and break out month, day, hour from date
    for i in range(len(date_list)):
        date_full = date_list[i]
        date = datetime.datetime.strptime(date_full, '%Y-%m-%d %H:%M')

        # Add 1 to the hour because renewableNinja gives hours on 0-23 scale
        # and we want 1-24 scale
        hour_adjusted = date.hour + 1

        # Shift time values to match BC time (ie. Shift 3pm Alberta time back
        # one hour, so all timeslices represent the asme time)
        # pylint: disable=protected-access
        hour_adjusted = hour_adjusted - functions._PROVINCIAL_TIME_ZONES[province]
        if hour_adjusted < 1:
            hour_adjusted = hour_adjusted + 24

        #Save data
        data.append(
            [province, date.month, date.day, hour_adjusted, cf_list[i]])

    #dataframe to output
    df_out = pd.DataFrame(data,
        columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])
    return df_out

def monthly_average_cf(df_in):
    """Geneartes a monthly representative day factor dataframe.

    Aggregates a hourly capcaity factor value given over a year, to a
    representative day capacity factor value given over a season.

    Args:
        df_in: Dataframe giving the hourly capacpity factor for a year
            (columns = province, month, hour, value)

    Returns:
        df_out: Dataframe giving the average day per month
            (columns = province, month, hour, value)
    """

    #Values to filter over
    months = range(1,13)
    hours = range(1,25)

    #List to hold all data in to be written to a dataframe
    data = []

    #filter input dataframe to show all hours for one month
    for month in months:
        for hour in hours:
            df_temp = df_in.loc[(df_in['MONTH']==month) &
                                (df_in['HOUR']==hour)]
            df_temp.reset_index(drop=True, inplace=True)
            data.append(
                [df_in['PROVINCE'].iloc[0],
                month,
                hour,
                df_temp['VALUE'].mean()])

    #dataframe to output
    df_out = pd.DataFrame(data, columns = ['PROVINCE','MONTH','HOUR','VALUE'])
    return df_out

def seasonal_average_cf(df_in, seasons):
    """Geneartes a seasonal representative day capacity factor dataframe.

    Aggregates a representative day capcaity factor value given over a month,
    to a representative day capacity factor value given over a season.

    Args:
        df_in: Dataframe giving the average day per month
            (columns = province, month, hour, value)
        seasons: Dictionary showing season to month mapping

    Returns:
        df_out: Dataframe giving the average day per season
            (columns = province, season, hour, value)
    """

    #Valeus to iterate over
    hours = range(1,25)

    #List to hold all data in to be written to a dataframe
    data = []

    #filter input dataframe to show all hours for one month
    for season in seasons:
        for hour in hours:
            cf = 0
            for month in seasons[season]:
                df_temp = df_in.loc[(df_in['MONTH'] == month) &
                                    (df_in['HOUR']==hour)]
                df_temp.reset_index(drop=True, inplace=True)
                cf = cf + df_temp.loc[0,'VALUE']
            cf = cf/len(seasons[season])
            data.append([df_in['PROVINCE'].iloc[0], season, hour, cf])

    #dataframe to output
    df_out = pd.DataFrame(data,columns = ['PROVINCE','SEASON','HOUR','VALUE'])
    return df_out

def read_nrel(subregions, seasons, years):
    """ Generates capacity factor values from NREL dataset.

    Reads in a raw NREL excel data file and parses the capacity factor values
    for thermal generation stations.

    Args:
        subregions: Dictionary for subregion to province mapping
        seasons: Dictionary for season to month mapping
        years: List of years to populate data for

    Returns:
        df_out: otoole formatted dataframe holding capacity factor values

    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    hour_list = range(1,25)

    #global filtering options
    scenario = 'Moderate'
    crp_years = 20
    metric_case = 'Market'

    # Dictionary key is technology abbreviation in our model
    # Dictionay value list holds how to filter input data frame
    # Max three list values match to columns [technology, techdetail, Alias]
    technology = {
        'COA':['Coal', 'IGCCHighCF'] ,
        'COC':['Coal', 'CCS30HighCF'] ,
        'CCG': ['NaturalGas','CCHighCF'],
        'CTG': ['NaturalGas','CTHighCF'],
        'URN': ['Nuclear'],
        'BIO': ['Biopower','Dedicated'],
    }

    #read in file
    source_file = '../dataSources/NREL_Costs.csv'
    df_raw = pd.read_csv(source_file, index_col=0)

    #filter out all numbers not associated with atb 2020 study
    df_raw = df_raw.loc[df_raw['atb_year'] == 2020]

    #drop all columns not needed
    df_raw.drop(
        ['atb_year','core_metric_key','Default'], axis=1, inplace=True)

    #apply global filters
    df_filtered = df_raw.loc[
        (df_raw['core_metric_case'] == metric_case) &
        (df_raw['crpyears'] == crp_years) &
        (df_raw['scenario'] == scenario)]

    #apply capacity factor filter
    df_cf = df_filtered.loc[df_filtered['core_metric_parameter'] == 'CF']

    #List to hold all output data
    #columns = ['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE']
    data = []

    #used for numerical indexing over columns shown in cost type for loop
    col_names = list(df_cf)

    #Loop over regions and years
    for subregion in subregions:
        for year in years:

            #filter based on years
            df_year = df_cf.loc[df_cf['core_metric_variable'] == year]

            #loop over technologies that contribute to total cost
            for tech, tech_filter in technology.items():

                #Filter to get desired technology
                df_tech = df_year
                for i in range(len(tech_filter)):
                    df_tech = df_tech.loc[
                        df_tech[col_names[i+3]] == tech_filter[i]]

                #There should only be one line item left at this point
                if len(df_tech) > 1:
                    print(f'There are {len(df_tech)} rows in the {year} \
                        {tech} dataframe')
                    print('DATA NOT WRITTEN!')
                    sys.exit()
                elif len(df_tech) < 1:
                    print(f'{tech} has a capacity factor of one in {year} \
                        for the {subregion} region')
                    cf = 1
                else:
                    #extract capaity factor
                    cf = df_tech.iloc[0]['value']
                    cf = round(cf,3)

                #write data for all timeslices in the year
                for season in seasons:
                    for hour in hour_list:
                        ts = season + str(hour)
                        tech_name = 'PWR' + tech + 'CAN' + subregion + '01'
                        data.append([continent, tech_name, ts, year, cf])

    df = pd.DataFrame(data,
        columns=['REGION','TECHNOLOGY','TIMESLICE','YEAR','VALUE'])
    return df

if __name__ == '__main__':
    main()
