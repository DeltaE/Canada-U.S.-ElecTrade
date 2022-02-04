import pandas as pd

def main():
    # PURPOSE: Creates otoole formatted TotalAnnualMaxCapacity.csv
    # INPUT: none
    # OUTPUT: none

    outputDir = '../src/data/TotalAnnualMaxCapacity.csv'  

    df = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    df.to_csv(outputDir, index=False)

if __name__ == "__main__":
    main()