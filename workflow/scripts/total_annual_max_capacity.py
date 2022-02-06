"""Creates total annual max capacity data"""

import pandas as pd
from pathlib import Path


def main():
    """Creates total annual max capacity data"""

    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/TotalAnnualMaxCapacity.csv')

    df = pd.DataFrame(columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    df.to_csv(output_dir, index=False)


if __name__ == '__main__':
    main()
