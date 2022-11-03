# mySql Server Configuration

Tested with mySql Server version 8.0.33 on a Mac Laptop running OSX 12.6.

The mySql server must be configured to allow:
* local disk access to write/read CSV files
* "strict mode" to be turned off, so CSV files can be imported via mysqlimport without exact matching of primary key values.


## Server Config Installation

* The file "my.cnf" should be placed in /etc/my.cnf