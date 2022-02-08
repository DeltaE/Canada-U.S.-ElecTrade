"""Creates all cost files"""

import pandas as pd
import functions
import sys
from pathlib import Path


def main():
    """Creates CAPEX, fixed, and variable costs otoole files.

    Generates capital cost, fixed cost and variable cost parameters files.
    Canadian values come from the NREL database and assumes no geographical
    weighting on costs. United States values are taken from origianl dataset
    and do include capital cost weighting factors.
    """

    # PARAMETERS

    can_subregions = functions.get_from_yaml('regions_dict')['CAN'].keys()
    years = functions.get_years()

    #Trigger used to print capital, fixed and variable costs one at a time
    for trigger in range(1, 4):

        #Cost type
        if trigger == 1:
            cost_type = ['CAPEX']
            df_usa = get_usa_capital_cost()
            out_file = 'CapitalCost.csv'
        elif trigger == 2:
            cost_type = ['Fixed O&M']
            df_usa = get_usa_fixed_cost()
            out_file = 'FixedCost.csv'
        elif trigger == 3:
            cost_type = ['Variable O&M', 'Fuel']
            df_usa = get_usa_variable_cost()
            out_file = 'VariableCost.csv'
        else:
            print('Need to select a cost type. SCRIPT NOT RUN!')
            sys.exit()

        # COST CALCULATIONS

        #reads the NREL raw datafile and extracts costs
        df_nrel = read_nrel(cost_type, can_subregions, years)

        #Populate Trade costs
        df_trade = trade_costs(cost_type, years)

        # WRITE DATA

        if trigger == 3:  # Variable costs have mode parameter
            df = pd.DataFrame(columns=[
                'REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION', 'YEAR', 'VALUE'
            ])
        else:
            df = pd.DataFrame(
                columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])

        df = df.append(df_nrel)
        df = df.append(df_trade)
        df = df.append(df_usa)

        output_dir = Path(Path(__file__).resolve().parent,
            '../../results/data', out_file)
        df.to_csv(output_dir, index=False)


def read_nrel(cost_type, subregions, years):
    """Parses the NREL datafile to extract technology costs.

    Reads in the NREL datafile and filters it to identify moderate, market
    case scenarios. Capex and fixed cost vales are taken straight from the
    datafile. Variable costs are assembles using both variable operation and
    fuel costs.

    Args:
        cost_type: List holding how to filter core_metric_parameter column
        regions: List holding what regions to print values over
        subregions: List holding what subregions to print values over
        years: list holding what years to print data over

    Returns:
        df_out: otoole formatted dataframe holding cost values

    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')

    # Nrel filetering parameters
    scenario = 'Moderate'
    crp_years = 20
    metric_case = 'Market'

    # Dictionary key is technology abbreviation in our model
    # Dictionay value list holds how to filter input data frame
    # Max three list values match to columns [technology, techdetail, Alias]
    technology = {
        'COA': ['Coal', 'IGCCHighCF'],
        'COC': ['Coal', 'CCS30HighCF'],
        'HYD': ['Hydropower', 'NPD4'],
        'CCG': ['NaturalGas', 'CCHighCF'],
        'CTG': ['NaturalGas', 'CTHighCF'],
        'WND': ['LandbasedWind', 'LTRG4'],
        'SPV': ['UtilityPV', 'KansasCity'],
        'URN': ['Nuclear'],
        'BIO': ['Biopower', 'Dedicated'],
    }

    # Dictionary for converting given units
    # CAPX: $/kW -> (1000*1000) -> $/GW -> (x10^-6) -> M$/GW
    # Fixed O&M: $/kW-yr -> $/kW -> (1000*1000) -> $/GW -> (x10^-6) -> M$/GW
    # Variable O&M: $/MWh -> ((1/3600)*1000*1000*1000) -> $/PJ ->
    #   (x10^-6) -> M$/PJ
    # Fuel: $/MMBtu -> ((1MMBtu/293.07kWh)*(1/3600)*1000*1000*1000*1000) ->
    #   $/PJ -> (x10^-6) -> M$/PJ
    unit_conv = {
        'CAPEX': 1,
        'Fixed O&M': 1,
        'Variable O&M': 0.277778,
        'Fuel': 0.94782058
    }

    #read in file
    df_raw = pd.read_csv(Path(Path(__file__).resolve().parent,
        '../../resources/NREL_Costs.csv'), index_col=0)

    #filter out all numbers not associated with atb 2020 study
    df_raw = df_raw.loc[df_raw['atb_year'] == 2020]

    #drop all columns not needed
    df_raw.drop(['atb_year', 'core_metric_key', 'Default'],
                axis=1,
                inplace=True)

    #apply global filters
    df_filtered = df_raw.loc[(df_raw['core_metric_case'] == metric_case)
                             & (df_raw['crpyears'] == crp_years) &
                             (df_raw['scenario'] == scenario)]

    #apply cost type filtering (capital, fixed, variable)
    df_cost = pd.DataFrame(columns=list(df_filtered))
    for cost in cost_type:
        df_temp = df_filtered.loc[df_filtered['core_metric_parameter'] == cost]
        df_cost = df_cost.append(df_temp)

    #List to hold all output data
    #columns = region, technology, year, value
    data = []

    #used for numerical indexing over columns shown in cost type for loop
    col_names = list(df_cost)

    #Technologies that operate on two modes of operation
    mode_two_techs = ['CCG', 'CTG', 'COA', 'COC', 'URN']

    #Loop over regions and years
    for subregion in subregions:
        for year in years:

            #filter based on years
            df_year = df_cost.loc[df_cost['core_metric_variable'] == year]

            #loop over technologies that contribute to total cost
            for tech, tech_filter in technology.items():

                #Filter to get desired technology
                df_tech = df_year
                for i in range(len(tech_filter)):
                    df_tech = df_tech.loc[df_tech[col_names[i + 3]] ==
                                          tech_filter[i]]

                #reset total cost
                total_cost = 0

                # For variable costs, we need to add variable cost and fuel cost
                for cost in cost_type:
                    df_end = df_tech.loc[df_tech['core_metric_parameter'] == cost]

                    # There should only be one (capital/fixed) or two
                    # (variable) line items left at this point
                    if len(df_end) > 1:
                        print(
                            f'There are {len(df_tech)} rows in the {year}'
                            f'{tech} dataframe for {cost_type[0]}'
                        )
                        print('DATA NOT WRITTEN!')
                        sys.exit()
                    elif len(df_end) < 1:
                        # print(f'{tech} has a {cost} cost of zero in {year}
                        # for the {region} region')
                        continue
                    else:
                        #calculate total cost
                        #handels edge case of nuclear fuel cost given in $/MWh
                        #####################################################
                        ###### HARD CODED IN ALL FULE UNITS TO BE MWh #######
                        ###### UNIT CONSISTENCY ISSUE ON ATB          #######
                        #####################################################
                        if tech == 'URN' and cost == 'Fuel':
                            total_cost = total_cost + (
                            df_end.iloc[0]['value'] * unit_conv['Variable O&M'])
                        elif tech == 'COA' and cost == 'Fuel':
                            total_cost = total_cost + (
                            df_end.iloc[0]['value'] * unit_conv['Variable O&M'])
                        elif tech == 'COC' and cost == 'Fuel':
                            total_cost = total_cost + (
                            df_end.iloc[0]['value'] * unit_conv['Variable O&M'])
                        elif tech == 'CCG' and cost == 'Fuel':
                            total_cost = total_cost + (
                            df_end.iloc[0]['value'] * unit_conv['Variable O&M'])
                        elif tech == 'CTG' and cost == 'Fuel':
                            total_cost = total_cost + (
                            df_end.iloc[0]['value'] * unit_conv['Variable O&M'])
                        else:
                            total_cost = total_cost + (
                            df_end.iloc[0]['value'] * unit_conv[cost])

                    total_cost = round(total_cost, 3)

                #construct technology name
                tech_name = 'PWR' + tech + 'CAN' + subregion + '01'

                # write data to output list
                # need to include a mode column for variable cost
                if cost_type[0] == 'Variable O&M':
                    if tech in mode_two_techs:
                        modes = [1, 2]
                    else:
                        modes = [1]
                    for mode in modes:
                        data.append(
                            [continent, tech_name, mode, year, total_cost])
                else:
                    data.append([continent, tech_name, year, total_cost])

    if cost_type[0] == 'Variable O&M':
        df = pd.DataFrame(data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION',
                              'YEAR', 'VALUE'
                          ])
    else:
        df = pd.DataFrame(data,
                          columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])

    return df


def p2g_system(cost_type, regions, subregions, years):
    """Generates power to gas system costs.

    Based on the cost type argument, will generate the power to gas system
    (electrolyzer and fuel cell) capital, fixed, or variable costs

    Args:
        cost_type: NREL cost type ('Fixed O&M', 'Fuel', ... )
        regions: List holding what regions to print values over
        subregions: List holding what subregions to print values over
        years: list holding what years to print data over

    Returns:
        df_out: otoole formatted dataframe holding cost values
    """

    #read in excel file
    source_file =  Path(Path(__file__).resolve().parent,
        '../../resources/P2G_FC_Costs.xlsx')
    df_p2g = pd.read_excel(source_file, sheet_name='P2G', index_col=0)
    df_fc = pd.read_excel(source_file, sheet_name='FC', index_col=0)

    # list to hold values
    data_p2g = []
    data_fc = []

    # populate lists
    for region in regions:
        for year in years:
            for subregion in subregions:

                #reset costs
                p2g_cost = 0
                fc_cost = 0

                #get costs
                for cost in cost_type:
                    p2g_cost = p2g_cost + df_p2g.loc[year, cost]
                    fc_cost = fc_cost + df_fc.loc[year, cost]

                #create tech names
                p2g_name = 'PWR' + 'P2G' + 'CAN' + subregion + '01'
                fc_name = 'PWR' + 'FCL' + 'CAN' + subregion + '01'

                # save data
                if cost_type[0] == 'Variable O&M':  #add in mode 1
                    data_p2g.append([region, p2g_name, 1, year, p2g_cost])
                    data_fc.append([region, fc_name, 1, year, fc_cost])
                else:
                    data_p2g.append([region, p2g_name, year, p2g_cost])
                    data_fc.append([region, fc_name, year, fc_cost])

    #create a master list to hold all data
    data = data_p2g
    data.extend(data_fc)

    #return completed dataframe
    if cost_type[0] == 'Variable O&M':  #Mode column
        df = pd.DataFrame(data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION',
                              'YEAR', 'VALUE'
                          ])
    else:
        df = pd.DataFrame(data,
                          columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    return df


def trade_costs(cost_type, years):
    """Generates electrial transmission costs for both countries.

    Based on the cost type argument, will generate the electrial transmission
    capital, fixed, or variable costs. This value is the same for all years
    and based on approximated distance between subregions.

    Args:
        cost_type: NREL cost type ('Fixed O&M', 'Fuel', ... )
        regions: List holding what regions to print values over
        years: list holding what years to print data over

    Returns:
        df_out: otoole formatted dataframe holding cost values
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')

    # Read in the trade csv file which contains costs
    df = pd.read_csv(Path(Path(__file__).resolve().parent,
        '../../resources/Trade.csv'))

    #Cost data only populated on mode 1 data rows
    df = df.loc[df['MODE'] == 1]

    # get list of all the technologies
    tech_list = df['TECHNOLOGY'].tolist()

    #List to hold all output data
    # columns = region, technology, year, value
    data = []

    #populate data
    for tech in tech_list:

        #remove all rows except for our technology
        df_cost = df.loc[df['TECHNOLOGY'] == tech]
        df_cost.reset_index()

        trn_cost = 0  #reset costs
        for cost in cost_type:
            trn_cost = trn_cost + float(df_cost[cost].iloc[0])

        #save same value for all years
        if cost_type[0] == 'Variable O&M':  # Include mode column
            for year in years:
                data.append([continent, tech, 1, year, trn_cost])
                data.append([continent, tech, 2, year, trn_cost])
        else:
            for year in years:
                data.append([continent, tech, year, trn_cost])

    if cost_type[0] == 'Variable O&M':
        df_out = pd.DataFrame(data,
                              columns=[
                                  'REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION',
                                  'YEAR', 'VALUE'
                              ])
    else:
        df_out = pd.DataFrame(
            data, columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    return df_out


def get_usa_capital_cost():
    """Gets capital costs (excluding transmission) for USA data.

    Returns:
        df_out = otoole formatted dataframe holding cost values
    """

    # PARAMETERS

    tech_map = functions.get_from_yaml('usa_tech_map')
    continent = functions.get_from_yaml('continent')

    # Read in USA files
    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'), sheet_name='CapitalCost(r,t,y)')

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
        value = df['CAPITALCOST'].iloc[i]
        value = round(value, 3)
        #Convert from $/kW to M$/GW

        out_data.append([continent, tech, year, value])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
                          columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    return df_out


def get_usa_fixed_cost():
    """Gets fixed costs (excluding transmission) for USA data.

    Returns:
        df_out = otoole formatted dataframe holding cost values
    """

    tech_map = functions.get_from_yaml('usa_tech_map')
    continent = functions.get_from_yaml('continent')

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'), sheet_name='FixedCost(r,t,y)')

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
        value = df['FIXEDCOST'].iloc[i]
        value = round(value, 3)
        out_data.append([continent, tech, year, value])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
                          columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    return df_out


def get_usa_variable_cost():
    """Gets variable costs (excluding transmission) for USA data.

    Returns:
        df_out = otoole formatted dataframe holding cost values
    """

    tech_map = functions.get_from_yaml('usa_tech_map')
    input_fuel_map = functions.get_from_yaml('tech_to_fuel')
    int_fuel = functions.get_from_yaml(
        'mine_fuels')  #Fuels that have international trade options
    continent = functions.get_from_yaml('continent')

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'), sheet_name='VariableCost(r,t,m,y)')

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
        mode = 1
        value = df['VARIABLECOST'].iloc[i]
        value = round(value, 3)
        out_data.append([continent, tech, mode, year, value])
        #checks if need to write value for mode 2
        if input_fuel_map[tech_mapped] in int_fuel:
            mode = 2
            out_data.append([continent, tech, mode, year, value])

    #create and return datafram
    df_out = pd.DataFrame(
        out_data,
        columns=['REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION', 'YEAR', 'VALUE'])
    return df_out


if __name__ == '__main__':
    main()
