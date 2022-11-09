# mySql Server Configuration

Tested with mySql Server version 8.0.33 on a Mac Laptop running OSX 12.6.

The mySql server must be configured to allow:
* local disk access to write/read CSV files
* "strict mode" to be turned off, so CSV files can be imported via mysqlimport without exact matching of primary key values.

NOTE:  **On Mac OSX,  Excel input files should be placed in `/Users/Shared/` so that `mysqlimport` can read the CSV files.**  
* The DB User does not automatically have permissions to read the python user's file space. 
* All subfolders in `/Users/Shared/` should have permissions set to 755.   
* The folder containing the Excel files should have permissions set to 777.

## Server Config Installation

* The file "my.cnf" should be placed in `/etc/my.cnf`.