# Canada and United States Electricty System Model

Mitigating climate change will require Canada and the United States to significantly decarbonize their economies. Expanding electricity trade capacity between these countries could help each system decarbonize in a more cost-effective mannor. Greater electricity trade would enable both countries to leverage the most favorable low- and zero-carbon resources though utilizing geographical advantages seen in specific regions. 

This project utilizes the Open Source Energy Modeling System ([OSeMOSYS](https://github.com/OSeMOSYS)) to model the electricity system of all Canadain provinces and the Continental United States. OSeMOSYS is a long range, least-cost energy system optimization modelliong framework. It will determine investment and dispatch decisions to satisfy electricity demands at the lowest possible cost while complying with any imposed restrictions, such as emissions limitations or renewable energy initiatives. Furthermore, all data in this model is public and freely available. This project is fully open source and can be analyzed by any curious modeller! 

The repository is broken into three main folders, as described below. The [Wiki](https://github.com/DeltaE/Canada-U.S.-ElecTrade/wiki) associated with this repository also provides detailed information on the the model structure and the modelling methodology. 

## 1. src Folder
The source folder contains all componetes required to run the model. Instructions on how to run the model, and dependicies to run the model, can be found in this folder. 

## 2. dataSources Folder 
The data soucres folder holds all raw downloaded and aggregated datasets. The sources for each of the datasets can be found in the corresponding [Wiki](https://github.com/DeltaE/Canada-U.S.-ElecTrade/wiki) pages. 

## 3. scripts Folder
The scripts folder holds all scripts for pre-processing and post-processing data. The pre-processing scripts will take the raw data and clean, filter, and convert it into a usable format for OSeMOSYS. The post-processing scripts will take result files and display graphs. 
