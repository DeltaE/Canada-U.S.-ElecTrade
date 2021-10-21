# CanadaUSA.txt Diff Checker

## Description

Compares two files to make sure that they have the same unordered
contents. This is useful if you are refactoring, as CanadaUSA.txt
generates with the same lines when no changes are made to the model, BUT
the lines will not necessarily be in the same order.

## To Run

1. Put the old CanadaUSA.txt file in the Old Copy folder, and the new CanadaUSA.txt in the New Copy folder. (if the files you are comparing have different names than "CanadaUSA.txt", change it in the header of the .py file)

2. Run CanadaUsaTxtDiffCheck.py

## Interpretation:

In Results.txt, it will give a timestamp of when it was run. It will
also say that the lines are the same if that is the case. Otherwise, it
will list lines that were removed or added.
