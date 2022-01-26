# Canada-U.S.Model Scripts Folder

## Contents
Included in this folder are the scripts used to pre-process, and a folder for post-processing scripts. Info on each script can be found in the header files, and the src/snakemake file.

### Note on naming convention
In these scripts, these words are used to indicated different regional scales:

- Continent: The smallest scale. In this model there is only one; NAmerica. Note that this level is called REGION by OSeMOSYS, and so CSV files are populated with this in mind
- Region: Currently equivalent to 'country', this model has a US region and a Canada region
- Subregion: This model is broken up into many subregions (such as Mountain West, Mid-Atlantic, Midwest...) each of which contain one or more provinces
- Province: The smallest units in the model are provinces and states, which are all described as 'provinces' for consistency