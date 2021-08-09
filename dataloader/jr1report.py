import openpyxl
import collections
import os

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

    def __init__(self, workbook):
        self._workbook = openpyxl.load_workbook(filename=workbook, data_only=True)
        self._worksheet = self._workbook.active
        self._report_id = self._worksheet.cell(row=1, column=1).value
        self._reporting_period = self._worksheet.cell(row=5, column=1).value
        self._filename = os.path.basename(workbook)
    
    @property
    def filename(self):
        return self._filename
    
    @property
    def report_id(self):
        return self._report_id
    
    @property
    def begin_date(self):
        return self._reporting_period.split('to')[0].strip()

    @property
    def end_date(self):
        return self._reporting_period.split('to')[1].strip()
    
    @property
    def title_type(self):
        return 'J'
    
    def _header_row(self):
        """
        Returns the header row

        The header row for J1 (R4) report consists of 12 static
        columns and a variable number of date columns, depending
        on the reporting period. For a 12 month report, there will
        be 12 date columns (Jan - Dec).

        Note that the first two columns are not part of the report
        specification. They are included for later referencing
        when data is loaded into the database.
        """

        # Start with non-date columns, which are static, and then
        # append the date column headings
        header = ['report_id', 'title_type', 'title', 'publisher', 'platform',
            'doi', 'proprietary_id', 'print_issn', 'online_issn',
            'reporting_period_total', 'reporting_period_html',
            'reporting_period_pdf']
        start_month = int(self.begin_date.split('-')[1])
        end_month = int(self.end_date.split('-')[1])
        period_cols = self.PERIODS[start_month:end_month+1]
        for month in period_cols:
            header.append(month)

        return header

    def data_rows(self):
        """
        Returns the number of rows containing publication data.

        According to the COUNTER Code of Practice R4, publication data always
        starts at row 10 in the spreadsheet.
        """

        n = 0
        for row in self._worksheet.iter_rows(min_row=self.DATA_ROW_START, min_col=1,
            max_row=self.MAX_ROWS, max_col=1, values_only=True):
            if row[0] is None: # Done when the first cell in the row is blank
                break
            n += 1
            
        return range(self.DATA_ROW_START, self.DATA_ROW_START + n)
    
    def _data_cols(self):
        """
        Returns the number of data columns. The actual number of
        columns depends on the reporting period.
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
        Returns a complete row of publication data for the given row number.

        For a JR1 report covering twelve months of usage data (typically Jan-Dec),
        there will be 22 columns of data in the row. Reports containing less (or more)
        months of usage data will have less or more list items, respectively.
        """

        row_spec = collections.namedtuple('ReportRow', self._header_row())

        datarow = list()
        datarow.append(self.report_id)
        datarow.append(self.title_type)
        for row in self._worksheet.iter_cols(min_row=n, min_col=self.DATA_COL_START,
            max_row=n, max_col=len(self._data_cols()), values_only=True):
            for cell in row:
                if cell is None: # Check for empty cells
                    datarow.append(None)
                elif str(cell).isspace():
                    datarow.append(None)
                else:
                    datarow.append(str(cell).strip())
                            
        return row_spec._make(datarow)
