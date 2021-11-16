from dataloader.jr1report import JR1Report
from dataloader.tmreport import TitleMasterReport
from dataloader.counter5db import TitleReportTable, MetricTable, ReportInventoryTable
import sys, os, glob
import traceback

def write_error(err_msg):
    logfile = open('errors.log', 'at')
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
        print('Usage: python loader.py <report directory>')
    else:
        
        # Begin processing individual reports. If something 
        # goes wrong, write a log entry and move on to the
        # next report.
        reportdir = sys.argv[1]
        files = glob.glob('{}/*.xlsx'.format(reportdir))
        print('Processing {} files:'.format(len(files)))
        for f in files:
            try:

                # Run through the load routines sequentially.
                if os.path.basename(f).startswith('jr'):
                    report = JR1Report(f)
                if os.path.basename(f).startswith('tr'):
                    report = TitleMasterReport(f)
                
                # Check if spreadsheet has already been loaded.
                inv = ReportInventoryTable()
                is_loaded = inv.is_loaded(report)
                if not is_loaded:
                    print(os.path.basename(f))

                    # Process the data in the spreadsheet.
                    trt = TitleReportTable()
                    mt = MetricTable()
                    for n in report.data_rows():
                        row = report.get_row(n)
                        rowid = trt.insert(row, report.run_date)
                        mt.insert(row, rowid, report.begin_date, report.end_date, report.run_date)
                    
                    # Update the report inventory.
                    inv.insert(report)
                    inv = None
                    report = None

                    # Mark as processed.
                    os.rename(f, f + '.processed')
                    
            except Exception as e:
                write_error('{0}\n{1}'.format(f, traceback.format_exc()))
