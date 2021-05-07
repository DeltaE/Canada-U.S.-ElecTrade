# Canada-U.S.Model Scripts Folder

## Contents
Inlcuded in this folder are the scripts used to pre-process and post-process data 

## Pre-Processing Scripts

`AvailabilityFactor.py`  
Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor 

`CapacityFactor.py`  
Creates an otoole formatted CSV holding capacity factors for Solar, Wind, Hydro and Gas. If Hydro Capacity Factors are used, be sure to remove hydro availabilty factor

`SpecifiedDemandProfile.py`
Create an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time

`SpecifiedAnnualDemand.py`
Create an otoole formatted CSV holding the specified annual demand for the model

## Post-Processing Scripts

`W_ProductionAndDemandNOTrade_24_extended.py`