"""Generates Capacity to Activity Unit data"""

import pandas as pd
import functions

def main():
    """Generates Capacity to Activity Unit data.

    Creates otoole formatted CapacityToActivityUnit file for all power and
    mining technologies. ASSUMES ALL UNITS ARE GW AND PJ
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    techs_master = functions.get_from_yaml('techs_master')
    rnw_fuels = functions.get_from_yaml('rnw_fuels')
    mine_fuels = functions.get_from_yaml('mine_fuels')
    subregions = functions.get_from_yaml('regions_dict')

    technologies = functions.create_tech_df(
                        subregions, techs_master, mine_fuels, rnw_fuels,
                        '../dataSources/Trade.csv')
    technologies_list = technologies['VALUE'].tolist()

    # CREATES FILE

    #capacity to activity columns = Region, Technology, Value
    out_data = []

    # unit conversion from GWyr to PJ
    # 1 GW (1 TW / 1000 GW)*(1 PW / 1000 TW)*(8760 hrs / yr)*(3600 sec / 1 hr) = 31.536
    # If 1 GW of capacity works constantly throughout the year, it produced 31.536 PJ
    cap_act_unit = 31.536

    #populate list
    for tech in technologies_list:
        out_data.append([continent, tech, cap_act_unit])

    #write to csv
    df_out = pd.DataFrame(out_data, columns=['REGION','TECHNOLOGY','VALUE'])
    df_out.to_csv('../src/data/CapacityToActivityUnit.csv', index=False)

if __name__ == '__main__':
    main()
