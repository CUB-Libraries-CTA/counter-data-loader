import os, glob, sys
import openpyxl
from dataloader.jr1report import JR1Report
from dataloader.tmreport import TitleMasterReport
from dataloader.counter_db import PlatformTable

# For PyCharm Debugging
import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=6666, stdoutToServer=True, stderrToServer=True, suspend=False)

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
            raise Exception("JR1Report is no longer supported with version 5 of Counter specification.")
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
    files = glob.glob('TR*.xl*')
    files.sort()
    num_files = len(files)
    num_files_processed = 0
    platform_table = PlatformTable()
    platform_names = platform_table.get_platform_names()
    for f in files:
        num_files_processed += 1
        print(" ({0} of {1}): ".format(num_files_processed, num_files), end='')
        sourcefile = f
        try:
            source = CounterReport(f)
            report = source.report()
            report.print_stats()
            report_year = report.begin_date[0:4]
            report_range = report.begin_date[5:7] + report.end_date[5:7]
            if report.has_all_valid_rows() and report.has_valid_platforms(platform_names):
                targetfile = '{0}-{1}-{2}-{3}.xlsx'.format(
                    source.version,
                    report.platform.lower().replace(' ', '-').replace(':',''),
                    report_year,
                    report_range)
                os.rename(sourcefile, targetfile)
            elif not report.has_all_valid_rows():
                error_msg = '{0}:  is missing one of (Title, Publisher, Platform) on these rows: ['.format(f)
                invalid_rows = report.get_invalid_rows()
                for row in invalid_rows:
                    error_msg += ' {0}'.format(row)
                error_msg += ' ]\n\n'
                raise Exception(error_msg)
            else:
                invalid_platforms = report.get_invalid_platforms(platform_names)
                assert(len(invalid_platforms) > 0)
                error_msg = '{0}:  has these platforms not present in the platform_ref table: ['.format(f)
                for platform in invalid_platforms:
                    error_msg += ' "{0}"'.format(platform)
                error_msg += ' ]\n\n'
                raise Exception(error_msg)
        except Exception as e:
            logfile = open('errors.log', 'at')
            logfile.write('{0} | {1}\n'.format(f, e))
            logfile.close()
