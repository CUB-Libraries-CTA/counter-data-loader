import glob
import os
import sys
import traceback
from datetime import datetime

# For PyCharm Debugging
#import pydevd_pycharm

from dataloader.counter_db import BulkImport, TitleReportTable, MetricTable, ReportInventoryTable
from dataloader.jr1report import JR1Report
from dataloader.tmreport import TitleMasterReport

#pydevd_pycharm.settrace('localhost', port=6666, stdoutToServer=True, stderrToServer=True, suspend=False)

# Running this script requires two arguments representing the directory
# containing the Excel COUNTER reports and the year to process.
#
# Given that this is a batch process, each spreadsheet in turn will have
# data extracted and written to the database. Each of the main database
# tables will be loaded in sequence to ensure dependencies are maintained.

def write_error(err_msg):
    logfile = open('errors.log', 'at')
    logfile.write(datetime.now().isoformat() + '\n')
    logfile.write(err_msg + '\n')
    logfile.close()
    
if __name__ == "__main__":

    if len(sys.argv) == 1:
        print('Usage: python loader.py <report directory> <year>')
    else:
        
        # Begin processing individual reports. If something 
        # goes wrong, write a log entry and move on to the
        # next report.
        reportdir = sys.argv[1]
        reportyr = sys.argv[2]
        files = glob.glob('{0}/*{1}*.xlsx'.format(reportdir, reportyr))
        files.sort()

        trt = TitleReportTable()
        mt = MetricTable()
        inv = ReportInventoryTable()
        for f in files:
            try:

                # Instantiate the report instance according to the report
                # version, i.e. COUNTER R4 or R5. 
                if os.path.basename(f).startswith('jr'):
                    report = JR1Report(f)
                if os.path.basename(f).startswith('tr'):
                    report = TitleMasterReport(f)
                
                # Check if spreadsheet has already been loaded. A record of
                # which reports have been loaded and when is maintained in
                # the inventory table.
                is_loaded = inv.is_loaded(report)
                if not is_loaded:
                    print(os.path.basename(f))

                    # Process the data in the spreadsheet. The method currently
                    # used relies on the use of temporary tables that are bulk
                    # loaded from CSV versions of the spreadsheet data. Inserts
                    # and updates are then handled from the temp tables.
                    load_start = datetime.now().isoformat()

                    # First step is to export title and metric data from the report
                    # into equivalent CSV files.
                    report.export()

                    # Next step is bulk importing of CSV files into temp tables.
                    bi = BulkImport(reportdir)
                    bi.import_all()
                    
                    # Finally, perform inserts into main tables from the temps.
                    trt.insert_from_temp()
                    mt.insert_from_temp()

                    load_end = datetime.now().isoformat()
                    
                    # Update the report inventory.
                    inv.insert(report, load_start, load_end)

                    # Clean up.
                    report.close()
                    
            except Exception as e:
                write_error('{0}\n{1}'.format(f, traceback.format_exc()))
