# Canada and United States Electricty System Model

Mitigating climate change will require Canada and the United States to significantly decarbonize their economies. Expanding electricity trade capacity between these countries could help each system decarbonize in a more cost-effective manner. Greater electricity trade would enable both countries to leverage the most favorable low- and zero-carbon resources though utilizing geographical advantages seen in specific regions. 

This project utilizes the Open Source Energy Modeling System ([OSeMOSYS](https://github.com/OSeMOSYS)) to model the electricity system of all Canadian provinces and the Continental United States. OSeMOSYS is a long range, least-cost energy system optimization modelling framework. It will determine investment and dispatch decisions to satisfy electricity demands at the lowest possible cost while complying with any imposed restrictions, such as emissions limitations or renewable energy initiatives. Furthermore, all data in this model is public and freely available. This project is fully open source and can be analyzed by any curious modeller! 

The repository is organized with several main folders, following [snakemake repository organization guidelines](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#distribution-and-reproducibility) as described below. The [Wiki](https://github.com/DeltaE/Canada-U.S.-ElecTrade/wiki) associated with this repository also provides detailed information on the the model structure and the modelling methodology. 

## 1. github Folder
Contains Pylint, for linting the .py parts of the codebase.

## 2. config Folder
Contains config.yaml, a modifiable set of values that adjusts the settings of the model.

## 3. resources Folder
Contains all raw downloaded and aggregated input datasets. The sources for each of the datasets can be found in the corresponding [Wiki pages](https://github.com/DeltaE/Canada-U.S.-ElecTrade/wiki). Also contains the model file, osemosys_fast_TB, a modified version of the original [OSeMOSYS_fast](https://github.com/OSeMOSYS/OSeMOSYS_GNU_MathProg/tree/master/src#installation) code. Specific modifications are outlined in the [wiki](https://github.com/DeltaE/Canada-U.S.-ElecTrade/wiki). 

## 4. results Folder
Contains data CSV's, which are the results of processing through snakemake, and are further processed by otoole into CanadaUSA.txt (also in this folder). CanadaUSA.txt is the datafile that is fed into OSeMOSYS. To summarize:

/resources/
PROCESSED WITH SNAKEFILE (USING WORKFLOW) INTO
/results/data/
PROCESSED WITH SNAKEFILE (USING OTOOLE) INTO
/results/CanadaUSA.txt
PROCESSED WITH OSEMOSYS

## 5. tests Folder
Contains tests. Currently only contains a diff check that can be used for checking different versions of /results/CanadaUSA.txt files.

## 6. workflow Folder 
Contains all scripts that are used to turn initial resources into processed data. Also contains the snakefile (which is used to run the model) and appropriate information for running the snakefile. Also contains a /notebooks/ folder for post-processing.