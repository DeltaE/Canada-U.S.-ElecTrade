"""Creates all reserve margin related parametes"""

import pandas as pd
import functions

# MODULE CONSTANTS

# holds baseline reserve margin for each province based on NERC
# 10 percent for hydro dominated provinces
# 15 percent for thermal dominated regions
_PROVINCIAL_RESERVE_MARGIN = {
    'BC':1.10,
    'AB':1.15,
    'SK':1.15,
    'MB':1.10,
    'ON':1.15,
    'QC':1.10,
    'NB':1.15,
    'NL':1.10,
    'NS':1.15,
    'PE':1.15}


def main():
    """Creates reserve margin vales and tags appropitae fuels/techs

    Creates a reserve margin value that takes into account the temporal
    resolution reducing demand peaks. Tags any non-variable technology as
    contributing to the reserve margin. Tags end use fuel as the commodity
    to apply the reserve margin to. The actual reserve margin value is
    inlcuded in the reserve margin tag fuel value to.

    Workflow:
        1. Assign a value of 1 for all osemosys regions (NAmerica)
        2. Tag technologies that can contribute to RM with a 1
        3. Assign the reserve margin value (1.25 for example) to the end use
           fuel.
    """

    # RESERVE MARGIN

    rm = get_can_rm()
    df_rm_usa = get_usa_rm()

    df_rm = pd.DataFrame(rm,columns=['REGION','YEAR','VALUE'])
    df_rm = df_rm.append(df_rm_usa)
    df_rm.to_csv('../src/data/ReserveMargin.csv', index=False)

    # RESERVE MARGIN TAG FUEL

    rm_fuel = get_can_rm_tag_fuel()
    df_rm_fuel_usa = get_usa_rm_tag_fuel()

    df_rm_fuel = pd.DataFrame(rm_fuel,columns=['REGION','FUEL','YEAR','VALUE'])
    df_rm_fuel = df_rm_fuel.append(df_rm_fuel_usa)
    df_rm_fuel.to_csv('../src/data/ReserveMarginTagFuel.csv', index=False)

    # RESERVE MARGIN TAG TECH

    rm_tech = get_can_rm_tag_tech()
    df_rm_tech_usa = get_usa_rm_tag_tech()

    df_rm_tech = pd.DataFrame(rm_tech,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    df_rm_tech = df_rm_tech.append(df_rm_tech_usa)
    df_rm_tech.to_csv('../src/data/ReserveMarginTagTechnology.csv', index=False)

def get_can_rm_tag_tech():
    """Creates Canadian Reserve Margin Tag Technology.

    Returns:
        df_out: Canadian Reserve Margin Tag Technology Data
    """

    can_subregions = functions.get_from_yaml('regions_dict')['CAN']
    continent = functions.get_from_yaml('continent')
    tech_tags = functions.get_from_yaml('techs_master')
    variable_techs = functions.get_from_yaml('variable_techs')
    years = functions.get_years()

    # Make list of techs to tag by removing the non-dispachable techs from tech_tags
    tech_tags = [x for x in tech_tags if x not in variable_techs]

    #reserve margin Tag Technology = Region, Technology, Year, Value
    rm_tag_tech = []
    for subregion in can_subregions:
        for year in years:
            for tech in tech_tags:
                tech_name = 'PWR' + tech + 'CAN' + subregion + '01'
                rm_tag_tech.append([continent, tech_name, year, 1])

    return rm_tag_tech

def get_can_rm_tag_fuel():
    """Creates Canadian Reserve Margin Tag Fuel.

    The reserve margin tag fuel will tag the end use demand fuel to which the
    reserve margin will be applied to. It also includes the actual reserve
    margin value (ie. 1.25) to account for our naming convention.

    Returns:
        df_out: Canadian Reserve Margin Tag Fuel Data
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN']
    seasons = functions.get_from_yaml('seasons')
    years = functions.get_years()
    hours = range(1,25)

    # ACCOUNT FOR PEAK SQUISHING

    #Read in complited actual loads that have been cleaned for DST
    df_demand_raw = functions.get_load_values()

    #Dictionary to hold regions additional reserve margin needed.
    peak_squish_factor = {}

    #Filter demand dataframe for provinces in each region
    for subregion, provinces in can_subregions.items():
        df_region = pd.DataFrame(
            columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])

        #Lists to hold regional actual and max loads
        actual_loads = []
        time_sliced_loads = []

        for province in provinces:
            df_temp = df_demand_raw[(df_demand_raw['PROVINCE'] == province)]
            df_region = df_region.append(df_temp)

        # The average loads are based on seasons (Jan,Feb,Mar represented as one day)
        # We need to calculate average hourly loads for each season
        for season, months in seasons.items(): # pylint: disable=unused-variable
            df_season = pd.DataFrame(
                columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])
            for month in months:
                df_temp = df_region.loc[df_region['MONTH'] == month]
                df_season = df_season.append(df_temp)

            #Find hourly average for each seasson
            for hour in hours:
                df_hour = df_season.loc[df_season['HOUR']==hour]
                avg_demand = df_hour['VALUE'].mean()

                # Save all timesliced loads in a list. Dropping the season
                # and hour mapping as reserve magin is based on year
                time_sliced_loads.append(avg_demand)

        #Save all actual loads for region filtered
        actual_loads = df_region['VALUE'].tolist()

        #calculate peak squishing reserve margin factor
        peak_ts = max(time_sliced_loads)
        peak_actual = max(actual_loads)
        peak_squish = (peak_actual - peak_ts) / peak_actual

        #save the peak squishing factor
        #This needs to be added to every
        peak_squish_factor[subregion] = peak_squish

    # CALCULATE WEIGHTED BASELINE RESERVE MARGIN

    #Read in csv containing data
    source_file = '../dataSources/ProvincialAnnualDemand.csv'
    df_demand = pd.read_csv(source_file, index_col=0)

    # List to hold region reserve margins
    #Region, year, value
    rm_raw = []

    for subregion, provinces in can_subregions.items():
        for year in years:
            total_demand = 0
            region_rm = 0

            #get regional total demand
            for province in provinces:
                total_demand = total_demand + df_demand.loc[year, province]

            #weighted reserve margin based on NERC numbers
            for province in provinces:
                region_rm = region_rm + (
                    df_demand.loc[year, province] / total_demand) * (
                    _PROVINCIAL_RESERVE_MARGIN[province])

            #add in squishing factor
            region_rm = region_rm + peak_squish_factor[subregion]

            #save adjusted regional reserve margin
            rm_raw.append([subregion, year, region_rm])

    #reserve margin Tag Fuel = Region, Fuel, Year, Value
    rm_tag_fuel = []
    for i in range(len(rm_raw)):
        fuel_name = 'ELC' + 'CAN' + rm_raw[i][0] + '01'
        year = rm_raw[i][1]
        rm = rm_raw[i][2]
        rm = round(rm,3)
        rm_tag_fuel.append([continent, fuel_name, year, rm])

    return rm_tag_fuel

def get_can_rm():
    """Creates Canadian Reserve Margin File.

    This will only tag the osemsosy regions (NAmerica) as applying the
    reserve margin. The actula reserve margin value is in the reserve margin
    tag fule file.

    Returns:
        data_out: Canadian Reserve Margin Tag Technology Data
    """

    continent = functions.get_from_yaml('continent')
    years = functions.get_years()

    #Reserve Margin = Region, year, value
    rm = []
    for year in years:
        rm.append([continent, year, 1])

    return rm

def get_usa_rm_tag_tech():
    """Creates USA Reserve Margin Tag Technology.

    Returns:
        df_out: USA Reserve Margin Tag Technology Data
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    tech_map = functions.get_from_yaml('usa_tech_map')
    variable_techs = functions.get_from_yaml('variable_techs')
    years = functions.get_years()

    df = pd.read_excel('../dataSources/USA_Data.xlsx',
        sheet_name = 'ReserveMarginInTagTech(r,t,y)')

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    #list to hold output data
    out_data=[]

    #get list of american subregions
    usa_subregions = df['REGION']
    usa_subregions = list(set(usa_subregions))

    #populate data
    for tech_old in tech_map:
        for year in years:
            for subregion in usa_subregions:
                tech_mapped = tech_map[tech_old]
                tech = 'PWR' + tech_mapped + 'USA' + subregion + '01'
                if tech_mapped in variable_techs:
                    value = 0
                else:
                    value = 1
                out_data.append([continent,tech,year,value])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
        columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return df_out

def get_usa_rm_tag_fuel():
    """Creates USA Reserve Margin Tag Fuel.

    The reserve margin tag fuel will tag the end use demand fuel to which the
    reserve margin will be applied to. It also includes the actual reserve
    margin value (ie. 1.25) to account for our naming convention.

    Returns:
        df_out: USA Reserve Margin Tag Fuel Data
    """

    ##################################################
    # Account for peak squishing
    ##################################################

    # Region Dictionary
    usa_subregions = functions.get_from_yaml('regions_dict')['USA']
    continent = functions.get_from_yaml('continent')
    years = functions.get_years()

    # Should update this for individual provinces
    # should be 10 percent for hydro dominated provinces or
    # 15 percent for thermal dominated regions
    base_rm = {
        'NW':1.15,
        'CA':1.15,
        'MN':1.15,
        'SW':1.15,
        'CE':1.15,
        'TX':1.15,
        'MW':1.15,
        'AL':1.15,
        'MA':1.15,
        'SE':1.15,
        'FL':1.15,
        'NY':1.15,
        'NE':1.15
    }

    source_file = '../dataSources/USA_Demand.xlsx'
    df_demand = pd.read_excel(source_file, sheet_name='AnnualDemand')
    df_profile = pd.read_excel(source_file, sheet_name='HourlyDemand')

    #rename profile dataframe columns
    df_profile = df_profile.rename(columns={'CAL Demand (MWh)':'CA',
                                        #'CAR Demand (MWh)':'',
                                        'CENT Demand (MWh)':'CE',
                                        'FLA Demand (MWh)':'FL',
                                        'MIDA Demand (MWh)':'MA',
                                        'MIDW Demand (MWh)':'MW',
                                        'NE Demand (MWh)':'NE',
                                        'NW Demand (MWh)':'NW',
                                        'NY Demand (MWh)':'NY',
                                        'SE Demand (MWh)':'AL',
                                        'SW Demand (MWh)':'SW',
                                        'TEN Demand (MWh)':'SE',
                                        'TEX Demand (MWh)':'TX'})

    #Fill in overlapping regions (these will have the same reserve margin)
    df_profile = df_profile.drop(columns=['CAR Demand (MWh)'])
    df_profile['MN'] = df_profile['NW']

    #Get total annual demand
    annual_demand = {}
    for subregion, provinces in usa_subregions.items():
        regional_demand = 0
        for province in provinces:
            regional_demand = regional_demand + df_demand.loc[
                df_demand['Abr.']==province]['PJ'].sum()
            if province == 'MD': #DC not by default included in demand
                regional_demand = regional_demand + df_demand.loc[
                    df_demand['Abr.']=='DC']['PJ'].sum()
        annual_demand[subregion] = regional_demand

    #Normalize the load profiles
    max_demand_dict = {}
    for subregion in usa_subregions:
        max_demand = df_profile[subregion].max()
        total_demand = df_profile[subregion].sum()
        max_demand_dict[subregion] = max_demand / total_demand

    # Actual Peak Demand
    actual_peak = {}
    for subregion in usa_subregions:
        actual_peak[subregion] = max_demand_dict[subregion] * annual_demand[subregion]

    #Modeled peak Demand
    df_modeled_profile = pd.read_excel('../dataSources/USA_Data.xlsx',
        sheet_name = 'SpecifiedDemandProfile(r,f,l,y)')

    #remove everything except 2019
    df_modeled_profile = df_modeled_profile.loc[
        (df_modeled_profile['YEAR'] > 2018) &
        (df_modeled_profile['YEAR']< 2020)]
    df_modeled_profile.reset_index()

    #get max modelled peak
    modeled_peak = {}
    for subregion in usa_subregions:
        max_profile = df_modeled_profile.loc[
            (df_modeled_profile['REGION'] == subregion)]['DEMAND'].max()
        modeled_peak[subregion]=max_profile * annual_demand[subregion] * (96/8960)

    #calculate adjusted reserve margin
    rm = {}
    for subregion in usa_subregions:
        rm[subregion] = base_rm[subregion] + (
            actual_peak[subregion] - modeled_peak[subregion]) / actual_peak[subregion]

    #list to hold output data
    out_data=[]

    #populate data
    for year in years:
        for subregion in usa_subregions:
            fuel = 'ELC' + 'USA' + subregion + '01'
            value = rm[subregion]
            out_data.append([continent,fuel,year,value])

    #create and return datafram
    df_out = pd.DataFrame(out_data, columns=['REGION','FUEL','YEAR','VALUE'])
    return df_out

def get_usa_rm():
    """Creates USA Reserve Margin File.

    This will only tag the osemsosy regions (NAmerica) as applying the
    reserve margin. The actula reserve margin value is in the reserve margin
    tag fule file.

    Returns:
        df_out: Canadian Reserve Margin Tag Technology Data
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    years = functions.get_years()

    #this one is easier to manually do...
    out_data = []

    for year in years:
        out_data.append([continent,year,1])

    #create and return datafram
    df_out = pd.DataFrame(out_data, columns=['REGION','YEAR','VALUE'])
    return df_out

if __name__ == '__main__':
    main()
