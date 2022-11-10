import os, glob, sys
import openpyxl
from dataloader.jr1report import JR1Report
from dataloader.tmreport import TitleMasterReport

# For PyCharm Debugging
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=6666, stdoutToServer=True, stderrToServer=True, suspend=False)

# The purpose of this script is to do a bulk renaming of COUNTER Excel
# files prior to loading. Applying a consistent naming convention serves
# a number of purposes including sorting and listing of files, and embedding
# meta information that may be useful for easy identification and troubleshooting.
# 
# The first step in the renaming process is to copy all files to be loaded into
# a working directory, separate from where they are normally kept on the Q: drive.
# The following code assumes all files are Excel (.xlsx) files. The common file
# is constructed from data contained within the Excel file itself:
#
# <version>-<platform>-<year>-<date range>.xlsx
#
# For example, a 2015 JR1 report from the ACM for the period Jan-Dec would be
# renamed as follows:
#
# jr1-acm-digital-library-2015-0112.xlsx
#
# Once all the files have been renamed, they can be processed. If any errors
# occur, the offending file will be logged in an error log.

class CounterReport:
    """
    Represents a COUNTER report in Excel format.
    """
    def __init__(self, file):
        self._workbook = openpyxl.load_workbook(filename=file, data_only=True)
        self._worksheet = self._workbook.active
        self._a1 = self._worksheet.cell(row=1, column=1).value
        self._version = None
        self._report = None
        if self._a1.startswith('Journal Report 1'):
            self._report = JR1Report(file)
            self._version = 'jr1'
        elif self._a1 == 'Report_Name':
            self._report = TitleMasterReport(file)
            self._version = self._report.report_id.lower().replace('_', '-')
        else:
            raise Exception
    
    def report(self):
        return self._report
    
    @property
    def version(self):
        return self._version

if __name__ == "__main__":

    os.chdir(sys.argv[1])
    files = glob.glob('*.xlsx')
    for f in files:
        sourcefile = f
        try:
            source = CounterReport(f)
            report = source.report()
            report_year = report.begin_date[0:4]
            report_range = report.begin_date[5:7] + report.end_date[5:7]
            if report.has_valid_rows():
                targetfile = '{0}-{1}-{2}-{3}.xlsx'.format(
                    source.version,
                    report.platform.lower().replace(' ', '-').replace(':',''),
                    report_year,
                    report_range)
                os.rename(sourcefile, targetfile)
            else:
                error_msg = '{0}:  is missing part of (Title, Publisher, Platform) on these rows: [ '.format(f)
                invalid_rows = report.get_invalid_rows()
                for row in invalid_rows:
                    error_msg += ' {0}'.format(row)
                error_msg += ' ]\n\n'
                raise Exception(error_msg)
        except Exception as e:
            logfile = open('errors.log', 'at')
            logfile.write('{0} | {1}\n'.format(f, e))
            logfile.close()
