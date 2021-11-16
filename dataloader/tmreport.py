import openpyxl
import collections
import os

class TitleMasterReport:
    """
    Represents a Title Master Report.

    This class is able to load any of the standard views defined for the
    Title Master Report. Currently, only J1/J3 reports are loaded for
    journal titles and the B1/B3 reports for books. The type of standard view
    is specified in the header (Report_ID).
    """

    PERIODS = ['', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
        'sep', 'oct', 'nov', 'dec']
    MAX_ROWS = 1048576
    DATA_ROW_START = 15

    def __init__(self, workbook):
        self._workbook = openpyxl.load_workbook(filename=workbook, data_only=True)
        self._worksheet = self._workbook.active
        self._report_id = self._worksheet.cell(row=2, column=2).value
        self._reporting_period = self._worksheet.cell(row=10, column=2).value
        self._platform = self._worksheet.cell(row=15, column=4).value
        self._filename = os.path.basename(workbook)

    @property
    def filename(self):
        return self._filename

    @property
    def report_id(self):
        return self._report_id

    @property
    def begin_date(self):
        kv_pair = self._reporting_period.split(';')[0]
        return kv_pair.split('=')[1]

    @property
    def end_date(self):
        kv_pair = self._reporting_period.split(';')[1]
        return kv_pair.split('=')[1]
    
    @property
    def run_date(self):
        return self._worksheet.cell(row=11, column=2).value

    @property
    def title_type(self):
        return self.report_id[3:4]
    
    @property
    def platform(self):
        return self._platform

    @property
    def row_count(self):
        return len(self.data_rows())
    
    def _header_row(self):
        """
        Returns the report header row (column names).

        The header row is constructed from two pieces:

            - all the title identifying information (incl isbn and yop)
            - the usage period columns

        Access_Type may be included in either report type, e.g., in TR_B3 and
        TR_J3.

        For the date columns, the exact number (and range) depends on the
        reporting period of the report. In most cases, the reporting period
        will be January to December; however, the report could have been
        run for any period, e.g., April to July. Therefore, the begin and
        end dates for the reporting period will determine which month columns
        to include in the header.
        """

        # Build the title/book info columns by iterating through the spreadsheet
        # columns beginning with A (Title)
        #col = {'TR_J1': 11, 'TR_J3': 12, 'TR_B1': 13, 'TR_B3': 14}
        #header = ['report_id', 'title_type']
        header = ['report_id', 'title_type', 'title', 'publisher', 'publisher_id',
            'platform', 'doi', 'proprietary_id', 'isbn', 'print_issn', 'online_issn',
            'uri', 'yop', 'access_type', 'metric_type']
        start_month = int(self.begin_date[5:7])
        end_month = int(self.end_date[5:7])
        period_cols = self.PERIODS[start_month:end_month+1]
        for month in period_cols:
            header.append(month)

        return header

    def data_rows(self):
        """
        Returns the range of data rows. For all report types, this is rows
        15 and onwards. The actual number of rows in a given report is
        variable and depends on the publisher.
        """

        n = 0
        for row in self._worksheet.iter_rows(min_row=self.DATA_ROW_START, min_col=1,
            max_row=self.MAX_ROWS, max_col=1, values_only=True):
            if row[0] is None: # When no more data, the first cell in the row will be blank
                break
            n += 1

        return range(self.DATA_ROW_START, self.DATA_ROW_START + n)

    def _data_cols(self):
        """
        Returns the range of data columns. The actual number of columns
        depends on the report type.
        """

        n = 0
        for col in self._worksheet.iter_cols(min_row=self.HEADER_ROW,
            min_col=self.DATA_COL_START, max_row=self.HEADER_ROW,
            max_col=self.MAX_COLS, values_only=True):
            if col[0] is None:
                break
            n += 1

        return range(self.DATA_COL_START, self.DATA_COL_START + n)

    def get_row(self, n):
        """
        Gets a data row from the spreadsheet for a given row number.

        The return value is a named tuple, which provides for more
        intuitive referencing of columns during inserts and updates.
        """

        row = self._worksheet[n]
        row_spec = collections.namedtuple('ReportRow', self._header_row())

        # Initialize the data row
        datarow = list()
        datarow.append(self.report_id)
        datarow.append(self.title_type)

        # Append the remaining column data
        i = 0
        while i < len(row):
            if i == 6 and self.title_type == 'J':
                datarow.append('') # isbn
            if i == 9 and self.title_type == 'J':
                datarow.append('') # yop
            if row[i].value is None:
                datarow.append('')
            else:
                datarow.append(str(row[i].value).strip())
            i += 1

        # Remove the total columns that are not used
        datarow = datarow[0:15] + datarow[16:]

        return row_spec._make(datarow)
