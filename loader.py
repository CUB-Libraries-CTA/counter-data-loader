from datetime import datetime
from dataloader.jr1report import JR1Report
from dataloader.tmreport import TitleMasterReport
from dataloader.counter5db import BulkImport, TitleReportTable, MetricTable, ReportInventoryTable
import sys, os, glob
import traceback

def write_error(err_msg):
    logfile = open('errors.log', 'at')
    logfile.write(datetime.now().isoformat() + '\n')
    logfile.write(err_msg + '\n')
    logfile.close()
    
if __name__ == "__main__":

    # Running this script requires a single argument representing
    # the directory containing the Excel COUNTER reports.
    #
    # Given that this is a batch process, each spreadsheet in turn
    # will have data extracted and written to the database. Each
    # of the main database tables will be loaded in sequence to
    # ensure dependencies are maintained.
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

                # Run through the load routines sequentially.
                if os.path.basename(f).startswith('jr'):
                    report = JR1Report(f)
                if os.path.basename(f).startswith('tr'):
                    report = TitleMasterReport(f)
                
                # Check if spreadsheet has already been loaded.
                is_loaded = inv.is_loaded(report)
                if not is_loaded:
                    print(os.path.basename(f))

                    # Process the data in the spreadsheet.
                    load_start = datetime.now().isoformat()
                    report.export(reportdir)
                    bi = BulkImport(reportdir)
                    bi.import_all()
                    trt.insert_from_temp()
                    mt.insert_from_temp()
                    load_end = datetime.now().isoformat()
                    
                    # Update the report inventory.
                    inv.insert(report, load_start, load_end)

                    # Clean up.
                    report.close()
                    
            except Exception as e:
                write_error('{0}\n{1}'.format(f, traceback.format_exc()))
