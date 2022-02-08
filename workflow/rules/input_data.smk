"""Holds rules for processing model input data."""

import itertools
from pathlib import Path


# PARMAETERS

configfile: 'config/config.yaml'
resources = 'resources'
scripts = '../scripts'
results = 'results'
canadaProvinces = list(itertools.chain.from_iterable(
	config['regions_dict']['CAN'].values()))

# RULES 

rule make_sets:
	input:
		Path(resources, 'Trade.csv'),
		Path(resources, 'USA_Data.xlsx'),
	output:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(results, 'data', 'EMISSION.csv'),
		Path(results, 'data', 'STORAGE.csv'),
		Path(results, 'data', 'TECHNOLOGY.csv'),
		Path(results, 'data', 'FUEL.csv')
	log:
		'logs/make_sets.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/make_sets.py'

rule availability_factor:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'AvailabilityFactor.csv')
	log:
		'logs/availability_factor.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/availability_factor.py'

rule capacity_factor:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'NREL_Costs.csv'),
		Path(resources, 'USA_Data.xlsx'),
		expand(Path(resources,'CapacityFactor/SPV_{province}.csv'), 
			province = canadaProvinces),
		expand(Path(resources, 'CapacityFactor/WND_{province}.csv'), 
			province = canadaProvinces)
	output:
		Path(results,'data', 'CapacityFactor.csv')
	log:
		'logs/capacity_factor.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/capacity_factor.py'

rule capacity_activity_unit:
	input:
		Path(results, 'data', 'REGION.csv'),
		Path(results, 'data', 'TECHNOLOGY.csv'),
		Path(resources, 'Trade.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'CapacityToActivityUnit.csv')
	log:
		'logs/capacity_activity_unit.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/capacity_activity_unit.py'

rule costs:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'NREL_Costs.csv'),
		Path(resources, 'P2G_FC_Costs.xlsx'),
		Path(resources, 'Trade.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'CapitalCost.csv'),
		Path(results, 'data', 'FixedCost.csv'),
		Path(results, 'data', 'VariableCost.csv')
	log:
		'logs/costs.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/costs.py'

rule emission_activity_ratio:
	input:
		Path(resources, 'EmissionActivityRatioByTechnology.csv'),
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'EmissionActivityRatio.csv')
	log:
		'logs/emission_activity_ratio.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/emission_activity_ratio.py'

rule in_out_activity_ratio:
	input:
		Path(resources, 'InputActivityRatioByTechnology.csv'), 
		Path(resources, 'OutputActivityRatioByTechnology.csv'),
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'Trade.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'InputActivityRatio.csv'),
		Path(results, 'data', 'OutputActivityRatio.csv')
	log:
		'logs/in_out_activity_ratio.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/in_out_activity_ratio.py'

rule reserve_margin:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'ProvincialAnnualDemand.csv'),
		Path(resources, 'USA_Demand.xlsx'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'ReserveMargin.csv'),
		Path(results, 'data', 'ReserveMarginTagTechnology.csv'),
		Path(results, 'data', 'ReserveMarginTagFuel.csv')
	log:
		'logs/reserve_margin.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/reserve_margin.py'

rule residual_capacity:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'OperationalLifeTechnology.csv'),
		Path(resources, 'ResidualCapacitiesByProvince.csv'),
		Path(resources, 'Trade.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'ResidualCapacity.csv'),
		Path(results, 'data', 'OperationalLife.csv')
	log:
		'logs/residual_capacity.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/residual_capacity.py'

rule specified_annual_demand:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'ProvincialAnnualDemand.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'SpecifiedAnnualDemand.csv')
	log:
		'logs/specified_annual_demand.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/specified_annual_demand.py'

rule specified_demand_profile:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'ProvincialHourlyLoads.xlsx'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'SpecifiedDemandProfile.csv')
	log:
		'logs/specified_demand_profile.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/specified_demand_profile.py'

rule storage_costs:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'CapitalCostStorage.csv')
	log:
		'logs/storage_costs.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/storage_costs.py'

rule storage_life:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'OperationalLifeStorage.csv')
	log:
		'logs/storage_life.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/storage_life.py'

rule emission_penalty:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'EmissionPenaltyByYear.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'EmissionsPenalty.csv')
	log:
		'logs/emission_penalty.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/emission_penalty.py'

rule re_tags:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'RETagTechnology.csv')
	log:
		'logs/re_tags.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/re_tags.py'

rule tech_to_from_storage:
	input:
		Path(results, 'data', 'YEAR.csv'),
		Path(results, 'data', 'REGION.csv'),
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'TechnologyToStorage.csv'),
		Path(results, 'data', 'TechnologyFromStorage.csv')
	log:
		'logs/tech_to_from_storage.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/tech_to_from_storage.py'

rule total_annual_max_capacity:
	input:
		Path(resources, 'USA_Data.xlsx')
	output:
		Path(results, 'data', 'TotalAnnualMaxCapacity.csv')
	log:
		'logs/total_annual_max_capacity.log'
	conda:
		'envs/input_data.yaml'
	script:
		f'{scripts}/total_annual_max_capacity.py'