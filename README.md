# IIEEC_work
Preprocessing files created for IIEEC, in the 1st Semester of 19/20, at IST, Lisbon

-----------------------------------------------------------------------------------
-----------------------------------------------------------------------------------
## File discretize_dates.py

* File to discretize dates in datasets.
* The file outputs the same dataset, but with dates discretized into 0, 1, 2, ...

### To run the file discretize_dates.py:

**python discretize_dates.py -h**: Run this to get usage of program, with description of inputs
**python discretize_dates.py -e**: Run this to get example of input file

-----------------------------------------------------------------------------------
-----------------------------------------------------------------------------------
## File fill_data.py

* File to fill the missing data using LOCF and then a backwards iteration.
* The time-series duration are limited until a certain maximum timestep defined as input.
* Each column can be discretized according to what user may specify in a proper input file with discretization intervals and labels for each column.

### To run the file fill_data.py:

**python fill_data.py -h**: Run this to get usage of program, with description of inputs

**python fill_data.py -e**: Run this to get example of input file, with description of actions that would be done by the program

**python fill_data.py -d**: Run this to get example of the discretization file

-----------------------------------------------------------------------------------