"""Rules for buildind and solving the model."""

from pathlib import Path


# PARAMETERS

configfile: 'config/config.yaml'
resources = 'resources'
results = 'results'
scenario_name = config['scenario']

# CONSTANTS

OSEMOSYS_FILES = [
	'AccumulatedAnnualDemand.csv',
	'AnnualEmissionLimit.csv',
	'AnnualExogenousEmission.csv',
	'AvailabilityFactor.csv',
	'CapacityFactor.csv',
	'CapacityOfOneTechnologyUnit.csv',
	'CapacityToActivityUnit.csv',
	'CapitalCost.csv',
	'CapitalCostStorage.csv',
	'Conversionld.csv',
	'Conversionlh.csv',
	'Conversionls.csv',
	'DAILYTIMEBRACKET.csv',
	'DaysInDayType.csv',
	'DaySplit.csv',
	'DAYTYPE.csv',
	'default_values.csv',
	'DepreciationMethod.csv',
	'DiscountRate.csv',
	'DiscountRateStorage.csv',
	'EMISSION.csv',
	'EmissionActivityRatio.csv',
	'EmissionsPenalty.csv',
	'FixedCost.csv',
	'FUEL.csv',
	'InputActivityRatio.csv',
	'MinStorageCharge.csv',
	'MODE_OF_OPERATION.csv',
	'ModelPeriodEmissionLimit.csv',
	'ModelPeriodExogenousEmission.csv',
	'OutputActivityRatio.csv',
	'OperationalLife.csv',
	'OperationalLifeStorage.csv',
	'REMinProductionTarget.csv',
	'REGION.csv',
	'ReserveMargin.csv',
	'ReserveMarginTagFuel.csv',
	'ReserveMarginTagTechnology.csv',
	'ResidualCapacity.csv',
	'ResidualStorageCapacity.csv',
	'RETagFuel.csv',
	'RETagTechnology.csv',
	'SEASON.csv',
	'SpecifiedAnnualDemand.csv',
	'SpecifiedDemandProfile.csv',
	'STORAGE.csv',
	'StorageLevelStart.csv',
	'StorageMaxChargeRate.csv',
	'StorageMaxDischargeRate.csv',
	'TECHNOLOGY.csv',
	'TechnologyFromStorage.csv',
	'TechnologyToStorage.csv',
	'TIMESLICE.csv',
	'TotalAnnualMaxCapacity.csv',
	'TotalAnnualMaxCapacityInvestment.csv',
	'TotalAnnualMinCapacity.csv',
	'TotalAnnualMinCapacityInvestment.csv',
	'TotalTechnologyAnnualActivityLowerLimit.csv',
	'TotalTechnologyAnnualActivityUpperLimit.csv',
	'TotalTechnologyModelPeriodActivityLowerLimit.csv',
	'TotalTechnologyModelPeriodActivityUpperLimit.csv',
	'TradeRoute.csv',
	'VariableCost.csv',
	'YEAR.csv',
	'YearSplit.csv'
]

# RUELS

rule otoole_convert:
	input:
		datapackage = Path(resources, 'datapackage.json'),
		csvFiles = expand(Path(results, 'data', '{osemosys_file}'), 
			osemosys_file = OSEMOSYS_FILES)
	output:
		Path(results, f'{scenario_name}.txt')
	log:
		'logs/otoole_convert.log'
	conda:
		'envs/model.yaml'
	shell:
		'otoole convert datapackage datafile '
		'{input.datapackage} {output} 2> {log}'

#rule create_lp:
#	input:
#		modelFile = Path(results, 'osemosys_fast_TB.txt'),
#		dataFile = Path(results, fileName, '.txt')
#	output:
#		Path(results, fileName, '.lp')
#	log:
#		'logs/create_lp.log'
#	shell:
#		'glpsol -m {input.modelFile} -d {input.dataFile} '
#		'--wlp {output} --check 2> {log}'

