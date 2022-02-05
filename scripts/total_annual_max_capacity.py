"""Creates total annual max capacity data"""

import pandas as pd


def main():
    """Creates total annual max capacity data"""

    output_dir = '../src/data/TotalAnnualMaxCapacity.csv'

    df = pd.DataFrame(columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    df.to_csv(output_dir, index=False)


if __name__ == '__main__':
    main()
