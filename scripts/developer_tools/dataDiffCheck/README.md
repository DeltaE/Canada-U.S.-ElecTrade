# CanadaUSA.txt Diff Checker

## Description

Compares two CanadaUSA.txt files to make sure that they have the same
unordered contents within each section. This is useful if you are refactoring,
as CanadaUSA.txt generates with the same lines when no changes are
made to the model, BUT the lines will not necessarily be in the same order.

## To Run

1. In a terminal, navigate to the directory that contains CanadaUsaTxtDiffCheck.py

2. Run the command  
  
python CanadaUsaTxtDiffCheck.py 'path/from/this/location/to/old/CanadaUSA.txt' 'path/from/this/location/to/new/CanadaUSA.txt'  
  
, where appropriate relative paths are subbed in for the two paths, for example 'Old Copy/CanadaUSA.txt' and 'New Copy/CanadaUSA.txt'

## Interpretation:

In Results.txt, it will give a timestamp of when it was run. For every given CSV file, it will say that the lines are the same if that is the case. Otherwise, it will list lines that were removed or added.