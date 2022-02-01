"""Global Constants."""

# Residual Hydro Capacity (GW) per province in 2017
# https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startYear=2017&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20170101
RESIDUAL_HYDRO_CAPACITY = {
    'BC': 15.407,
    'AB': 1.218,
    'SAS': 0.867,
    'MAN': 5.461,
    'ONT': 9.122,
    'QC': 40.438,
    'NB': 0.968,
    'NL': 6.762,
    'NS': 0.370,
    'PEI': 0.000
}

# Hydro generation (TWh) per province in 2017
# https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startMonth=01&cubeTimeFrame.startYear=2017&cubeTimeFrame.endMonth=12&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20171201
HYDRO_GENERATION = {
    'BC': 66.510,
    'AB': 2.050,
    'SAS': 3.862,
    'MAN': 35.991,
    'ONT': 39.492,
    'QC': 202.001,
    'NB': 2.583,
    'NL': 36.715,
    'NS': 0.849,
    'PEI': 0.000
}
