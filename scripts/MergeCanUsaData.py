import pandas as pd
import os

def main():
    # PURPOSE: Appends the USA data onto the bottom of Canada data
    # INPUT: none
    # OUTPUT: none

    canadaDataDir = '../src/data/Canada/'
    usaDataDir = '../src/data/USA/'
    outputDir = '../src/data/'   

    for each_csv in os.listdir(canadaDataDir):
        #if each_csv == 'default_values.csv':
        #    continue
        if each_csv in os.listdir(usaDataDir):
            dfCan = pd.read_csv(canadaDataDir + each_csv)
            dfUsa = pd.read_csv(usaDataDir + each_csv)
            dfFinal = dfCan.append(dfUsa)
        else:
            dfFinal = pd.read_csv(canadaDataDir + each_csv)
        dfFinal.to_csv(outputDir + each_csv, index=False)

if __name__ == "__main__":
    main()