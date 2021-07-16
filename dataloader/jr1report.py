import openpyxl
from datetime import datetime
import string, os

class JR1Report:
    """
    Represents the JR1 report spreadsheet.

    The JR1 report is defined by the COUNTER Code of Practice R4 specification.
    The layout and data requirements are very specific. The properties and methods
    defined in this class rely on adherence to this specification otherwise data
    anomalies may arise and/or code using this class may raise an exception.
    """

    PERIODS = ['', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
        'sep', 'oct', 'nov', 'dec']
    MAX_ROWS = 1048576
    MAX_COLS = 16384
    HEADER_ROW = 8
    DATA_ROW_START = 10
    DATA_COL_START = 1
    DATA_COL_END = 22

    def __init__(self, workbook):
        self._workbook = openpyxl.load_workbook(filename=workbook, data_only=True)
        self._worksheet = self._workbook.active
        self._reporting_period = self._worksheet.cell(row=5, column=1).value
        self._filename = os.path.basename(workbook)
    
    @property
    def filename(self):
        return self._filename
    
    @property
    def period_from(self):
        return self._reporting_period.split('to')[0].strip()

    @property
    def period_to(self):
        return self._reporting_period.split('to')[1].strip()

    def _header_row(self):
        """
        Returns the header row

        The header row for J1 (R4) report consists of 10 static
        columns and a variable number of date columns, depending
        on the reporting period. For a 12 month report, there will
        be 12 date columns (Jan - Dec).
        """

        # Start with non-date columns, which are static, and then
        # append the date column headings
        header = ['title', 'publisher', 'platform', 'doi',
            'proprietary_id', 'print_issn', 'online_issn']
        start_month = int(self.period_from.split('-')[1])
        end_month = int(self.period_to.split('-')[1])
        period_cols = self.PERIODS[start_month:end_month+1]
        for month in period_cols:
            header.append(month)

        return header

    def data_rows(self):
        """
        Returns the range of rows containing publication data.

        According to the COUNTER Code of Practice R4, publication data always
        starts at row 10 in the spreadsheet.
        """

        r = self.DATA_ROW_START
        for row in self._worksheet.iter_rows(min_row=self.DATA_ROW_START, min_col=1,
            max_row=self.MAX_ROWS, max_col=1, values_only=True):
            if row[0] is None:
                break
            r += 1
            
        return list(range(self.DATA_ROW_START, r))
    
    def data_cols(self):
        """
        Returns the range of data columns. The actual number of columns
        depends on the reporting period.
        """
        c = 1
        for col in self._worksheet.iter_cols(min_row=self.HEADER_ROW,
            min_col=self.DATA_COL_START, max_row=self.HEADER_ROW,
            max_col=self.MAX_COLS, values_only=True):
            if col[0] is None:
                break
            c += 1

        return list(range(self.DATA_COL_START,c))

    def get_row(self, n):
        """
        Returns a complete row of publication data for the given row number.

        For a JR1 report covering twelve months of usage data (typically Jan-Dec),
        there will be 22 columns of data in the row. Reports containing less (or more)
        months of usage data will have less or more list items, respectively.
        """

        datarow = list()
        for row in self._worksheet.iter_cols(min_row=n, min_col=1,
            max_row=n, max_col=self.DATA_COL_END):
            for cell in row:
                if cell.value is None: # Check for empty cells
                    datarow.append('')
                else:
                    datarow.append(str(cell.value).replace('"', '').strip())
        
        return datarow
