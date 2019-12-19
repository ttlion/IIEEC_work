# -*- coding: utf-8 -*-
"""
File to fill the missing data using LOCF and then a backwards iteration

The time-series duration are limited until a certain maximum timestep
defined as input

Each column can be discretized according to what user may specify in a proper
input file with discretization intervals and labels for each column

@author: Tiago Leão
"""

###########################################################################
###########################################################################
# Imports

import pandas as pd
import numpy as np
import csv
import sys

###########################################################################
###########################################################################
# Defs with usage and examples

def showUsage():
    print('usage: python fill_data.py inputFile.csv timestepMax [option] [discrFile.csv]\n')
    print('inputFile.csv: Input dataset in table format, in timeseries')
    print('timestepMax: number of maximum timesteps that are kept from the time-series inserted')
    print('option (0 or 1, default 1): 1 prints variables that were not discretized by the program, 0 does not')
    print('discrFile.csv (not mandatory): File with the discretizations to be made')
    print('\nImportant Note: To insert discrFile.csv as argument, option parameter must also be specified!')
    print('\nRun python fill_data.py -e for an example of input')
    print('Run python fill_data.py -d for detailed information on the format of discrFile.csv')
    return

def printExample():
    print('The input csv table must be in the format of the following example')
    print('The column dateStep, with the timesteps of the time-series, must be named exatcly dateStep, as the program uses the name of this column')
    print('In the following example, REFs 2, 3 and 15 would be completely filled. REF 10 would be removed')
    print('Example of Input:')
    
    print('+-----+----------+----------+----------+')
    print('| REF | dateStep | Feature1 | Feature2 |')
    print('+-----+----------+----------+----------+')
    print('| 2   | 0        | a        | A        |')
    print('+-----+----------+----------+----------+')
    print('| 2   | 1        |          |          |')
    print('+-----+----------+----------+----------+')
    print('| 2   | 2        | b        | B        |')
    print('+-----+----------+----------+----------+')
    print('| 3   | 0        |          |          |')
    print('+-----+----------+----------+----------+')
    print('| 3   | 1        | a        | s        |')
    print('+-----+----------+----------+----------+')
    print('| 3   | 2        |          |          |')
    print('+-----+----------+----------+----------+')
    print('| 10  | 0        |          |          |')
    print('+-----+----------+----------+----------+')
    print('| 10  | 1        |          |          |')
    print('+-----+----------+----------+----------+')
    print('| 15  | 0        |          |          |')
    print('+-----+----------+----------+----------+')
    print('| 15  | 1        | c        | p        |')
    print('+-----+----------+----------+----------+')
    
    return

def printDiscrInfo():
    print('*********************************************************')
    print('*********************************************************')
    print('Format of the discretization file (.csv):\n')
    print('Intervals')
    print('tag, values of edges of intervals separated by commas')
    print('...')
    print('tag, values of edges of intervals separated by commas')
    print('Labels')
    print('tag, labels for intervals separated by commas')
    print('...')
    print('tag, labels for intervals separated by commas')
    print('Associations')
    print('columnName,tag')
    print('...')
    print('columnName,tag')
    print('\n*********************************************************')
    print('Important notes:')
    print('   The rows named Intervals, Labels and Associations must have those names')
    print('   Tags can be any string as long as they are unique')
    print('   Labels can be any string as long as they are unique inside each tag')
    print('*********************************************************')
    print('*********************************************************')
    print('Example of discretization file:\n')
    print('Intervals')
    print('A,0,0.6,19')
    print('3,90,91.7,400,500,501')
    print('PP,-100,200,400,980.2')
    print('Labels')
    print('A,X,Y')
    print('3,A,AA,AAA,AAAA')
    print('Associations')
    print('columnName1,A')
    print('columnName2,PP')
    print('columnName3,A')
    print('columnName4,3')
    print('\n*********************************************************')
    print('The previous example will discretize columnName1, 2, 3 and 4 into:')
    print('   columnName1:')
    print('      [0, 0.6[ -> X')
    print('      [0.6, 19[ -> Y')
    print('   columnName2:')
    print('      [-100, 200[ -> 1')
    print('      [200, 400[ -> 2')
    print('      [400, 980.2[ -> 3')
    print('   columnName3:')
    print('      [0, 0.6[ -> X')
    print('      [0.6, 19[ -> Y')
    print('   columnName4:')
    print('      [90, 91.7[ -> A')
    print('      [91.7, 400[ -> AA')
    print('      [400, 500[ -> AAA')
    print('      [500, 501[ -> AAAA')
    print('*********************************************************')
    print('*********************************************************')
    
    return

###########################################################################
###########################################################################
# Check command line arguments validity

if len(sys.argv) == 2:
    if sys.argv[1] == '-h':
        showUsage()
        exit()
    elif sys.argv[1] == '-e':
        printExample()
        exit()
    elif sys.argv[1] == '-d':
        printDiscrInfo()
        exit()


if len(sys.argv) != 3 and len(sys.argv) != 4 and len(sys.argv) != 5:
    print('Arguments not properly inserted! Run with -h for usage')
    exit()

###########################################################################
###########################################################################
# Put in a dictionary the discretizations specified in a csv file if it was provided

discrDict = {} # have an empty dictionary by default

if(len(sys.argv) == 5):
    
    if sys.argv[4].find('.csv') == -1:
        print('File with discretizations must be .csv format! Run with -h for usage')
        exit()
    
    # Open the given input file with discretizations and parse the csv reader
    discrFile = open(sys.argv[4], newline='', encoding='utf-8-sig')
    csv_reader = csv.reader(discrFile, delimiter=',')
    
    # Read first line and check if it has 'Intervals'
    row = next(csv_reader)
    if(row[0]!='Intervals'):
        print('File with discretization does not start with \'Intervals\'')
        print('Run with -h for usage')
        exit()
    
    
    intervDict = {} # create an empty dictionary to store intervals and labels
    for row in csv_reader: # Read all the specified intervals   
        if(row[0]=='Labels'):
            break
        intervDict.update( { row[0] : [ np.asfarray(np.array(row[1:len(row)]),  float).tolist(), 
                                         np.arange(1,len(row)-1).tolist() ] } )
    
    
    for row in csv_reader: # Read all the specified labels
        if(row[0]=='Associations'):
            break
        
        if (len(row)-1) != len(intervDict[row[0]][1]):
            print('Incorrect number of labels for tag \'{}\'!' .format(row[0]) )
            print('   Expected {} labels but inserted {}' .format ( len(intervDict[row[0]][1]), (len(row)-1) ) )
            print('   Default integer labels from 1 to {} will be used' .format( intervDict[row[0]][1] ) )
            continue
        
        intervDict[row[0]][1] = row[1:len(row)]
    
    
    discrDict = {} # create an empty dictionary with the discretizations per column
    for row in csv_reader: # Associate column with the proper discretization
        if(len(row)!=2):
            print('Problem in discretization file in line {}' .format(row))
            print('Associations must be in the form \'ColumnName,tag\'')
            continue
        
        if row[1] not in intervDict:
            print('Tag {} was not specified!' .format(row[1]) )
            print('   Association {}:{} was not possible to create' .format(row[0], row[1]) )
            print('   Column {} will not be discretized'.format(row[0]) )
            continue
        
        discrDict.update( { row[0] : intervDict[row[1]] } )
    
    # Close input file
    discrFile.close()

###########################################################################
###########################################################################
# Get input and output files from terminal

if sys.argv[1].find('.csv') == -1:
    print('Input file must be .csv format! Run with -h for usage')
    exit()
    
inputpath = sys.argv[1]

inputpath_noextension = inputpath.replace('.csv','')
outputpath = inputpath_noextension + "_LOCF.csv" # exemplo

if int(sys.argv[2]) < 0:
    print('timestepMax cannot be negative! Run with -h for usage')
    exit()

timestepMax = int(sys.argv[2])


option = 1
if len(sys.argv) == 4:
    if int(sys.argv[3]) != 0 and int(sys.argv[3]) != 1:
        print('option argument must be either 0 or 1! Run with -h for usage')
        exit()
    option = int(sys.argv[3])


###########################################################################
###########################################################################
# Open, read and close input file

# Open input file
inputFile = open(inputpath, newline='', encoding='utf-8-sig')

# Read input file, putting patients REFs as indexes for each row
inputFileDataFrame = pd.read_csv(inputpath, sep = ',', index_col=0, header=0)

# Close input file
inputFile.close()

###########################################################################
###########################################################################
# Group data by index (which are the patients REFs)
data_grouped = inputFileDataFrame.groupby(inputFileDataFrame.index)

###########################################################################
###########################################################################
# Propagate values forwards using LOCF and then propagate backwards to use
# the as many values as possible

# This for loop and then the concat after the loop are needed beause if there
# is a patient only with Nan the pandas default functions will insert values
# into those collumns instead of keeping the Nans in those situations
storeEachGroup = [None] * (data_grouped.ngroups)
i=0
for name, group in data_grouped:
    storeEachGroup[i] = group.fillna(method = 'ffill', axis=0).fillna(method = 'bfill', axis=0)
    i+=1

data_with_LOCF = pd.concat(storeEachGroup) # Put all groups/patients together again

###########################################################################
###########################################################################
# Remove from the database all patients that have a Nan, because having the Nan
# means that, for some feature for that patient, there was not a single measurement
# in all time-series of that patient

data_with_LOCF = data_with_LOCF.dropna()

# Keep in the database only timesteps until a certain specified maximum
data_with_LOCF = data_with_LOCF[data_with_LOCF['dateStep'] <= timestepMax]

###########################################################################
###########################################################################
# Discretize each collumn in bins

storeEachCollumn = [None] * ( (data_with_LOCF.shape)[1] - 1)
k=0

for column in data_with_LOCF:
    
    if (column not in discrDict):
        if option == 1:
            print('Program did not discretize: ' + column);
        continue;
    
    storeEachCollumn[k] = pd.cut( data_with_LOCF[column], 
                                    bins = discrDict[column][0], 
                                    labels = discrDict[column][1], 
                                    include_lowest = True, right = False ).tolist()
    k+=1

    
k=0
for column in data_with_LOCF:
    
    if (column not in discrDict):
        continue;
    
    data_with_LOCF[column] = storeEachCollumn[k]
    k+=1
    
###########################################################################
###########################################################################
# Write new data into output file .csv

data_with_LOCF.to_csv(outputpath, encoding='utf-8-sig', index=True, sep=',')

"""
# This commented lines allow having some stats over the output dataset

data_grouped = data_with_LOCF.groupby(data_with_LOCF.index)

# Duration of the timeseries of each patient
seriesDurationPerRef_changed = data_grouped['dateStep'].agg('max').to_numpy()

# Number of patients
numberDifferentRefs_changed = data_grouped.ngroups
"""
