# Canada-U.S.-ElecTrade Model Results Diff Checker

## Description
Compares two sets of .CSV result files from src/data to make sure that they have the same contents (and lists changes if and where they occur).  This is useful if you are refactoring, so that you can make sure there has been no change in functionality of the model, or if you want to see where intentional or unintentional changes happened in the model.

## To Run
### 1. Put the contents of the old Canada-U.S.-ElecTrade/src/data file into the Old Copy folder, and the contents of the new Canada-U.S.-ElecTrade/src/data file into the New Copy folder.

### 2. Run CanadaUsaTxtDiffCheck.py

## Interpretation:
In Sheets Results.txt, it will give a timestamp of when it was run. For every given CSV file, it will say that the lines are the same if that is the case. Otherwise, it will list lines that were removed or added.