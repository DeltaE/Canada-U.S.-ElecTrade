"""Processes results from the list of CSV files

Notes
-----
This script process result CSVs from an OSeMOSYS model run and
generates interactive figures, as well as summary results tables
"""
import pandas as pd
import os
import sys
import plotly.express as px

from logging import getLogger

logger = getLogger(__name__)

def main(input_folder: str,
         output_folder: str,
         datapackage: str):
    """Process result CSVs and generate figures
    """
    
    name_color_codes = pd.read_csv(r'./config/color_codes.csv', 
                                   encoding='latin-1')
    tech_names = dict([(c, n) for c, n
                       in zip(name_color_codes.tech,
                              name_color_codes.tech_name)])
    color_dict = dict([(n, c) for n, c
                       in zip(name_color_codes.tech_name,
                              name_color_codes.colour)])
    
    df_totalcapacity = pd.DataFrame(columns=['COUNTRY',
                                             'TECHNOLOGY',
                                             'YEAR',
                                             'VALUE'])

    df_totalcapacity = table_capacity(os.path.join(input_folder,
                                                  'TotalCapacityAnnual.csv'),
                                      tech_names)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df_totalcapacity.to_csv(os.path.join(output_folder,
                                         'totalcapacity_agg.csv'),
                            index=False)
    plot_figure(df_totalcapacity,
                'totalcapacity',
                'COUNTRY',
                'VALUE',
                'TECHNOLOGY',
                'YEAR',
                'Country',
                'Gigawatts')


def ts_template(commodity, days_dict, seasons_dict):
    if commodity in ['Demand']:
        df_ts_template = pd.DataFrame(list(itertools.product(demands,
                                                             months,
                                                             hours,
                                                             years)
                                           ),
                                      columns=['FUEL', 'MONTH', 'HOUR', 'YEAR']
                                      )
    if commodity in ['Generation']:
        df_ts_template = pd.DataFrame(list(itertools.product(generation,
                                                             months,
                                                             hours,
                                                             years)
                                           ),
                                      columns=['FUEL', 'MONTH', 'HOUR', 'YEAR']
                                      )
    df_ts_template = df_ts_template.sort_values(by=['FUEL', 'YEAR'])
    df_ts_template['DAYS'] = df_ts_template['MONTH'].map(days_dict)
    df_ts_template['SEASON'] = df_ts_template['MONTH'].map(seasons_dict)
    df_ts_template['YEAR'] = df_ts_template['YEAR'].astype(int)

    return df_ts_template


def table_capacity(input_file,
                   tech_names):
    df = pd.read_csv(input_file)
    df = df.loc[df.TECHNOLOGY.str[0:3] == 'PWR']
    df['COUNTRY'] = df.TECHNOLOGY.str[6:9]
    df.TECHNOLOGY = df.TECHNOLOGY.str[3:6]
    #df.TECHNOLOGY = df.loc[~(df.TECHNOLOGY.isin(['TRN']))]
    df['TECHNOLOGY'].replace(tech_names,
                             inplace=True)
    df.VALUE = df.VALUE.astype('float64')
    df.drop(['REGION'],
            axis=1,
            inplace=True)
    output_df = df[['COUNTRY',
                    'TECHNOLOGY',
                    'YEAR',
                    'VALUE']]
    return output_df


def plot_figure(input_df, title,
                xaxis, yaxis, color,
                animation_frame,
                xtitle, ytitle):
    fig = px.bar(input_df,
                 x=xaxis,
                 y=yaxis,
                 animation_frame=animation_frame,
                 color=color)

    return fig.write_html(os.path.join(output_folder,
                                        title + '.html'))


if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    datapackage = sys.argv[3]
    main(input_folder, output_folder, datapackage)
