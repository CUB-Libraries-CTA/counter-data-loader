import openpyxl
from datetime import datetime
import string

class JR1Report:
    """
    Represents the JR1 report spreadsheet.

    The JR1 report is defined by the COUNTER Code of Practice R4 specification.
    The layout and data requirements are very specific. The properties and methods
    defined in this class rely on adherence to this specification otherwise data
    anomalies may arise and/or code using this class may raise an exception.
    """

    def __init__(self, workbook):
        self._workbook = openpyxl.load_workbook(filename=workbook, data_only=True)
        self._worksheet = self._workbook.active
    
    @property
    def platform(self):
        return self._worksheet.cell(row=10, column=3).value

    @property
    def period_from(self):
        period = self._worksheet.cell(row=5, column=1).value
        return datetime.strptime(period.strip()[:10], '%Y-%m-%d')

    @property
    def period_to(self):
        period = self._worksheet.cell(row=5, column=1).value
        return datetime.strptime(period.strip()[-10:], '%Y-%m-%d')

    def data_range(self):
        """
        Returns the range of rows containing publication data.

        According to the COUNTER Code of Practice R4 publication data always
        starts at row 10 in the spreadsheet.
        """

        row_num = 10
        for row in self._worksheet.iter_rows(min_row=10, min_col=1, max_row=10000, max_col=1):
            if row[0].value == None:
                break
            row_num = row_num + 1
        return range(10, row_num)
    
    def get_row(self, row_num):
        """
        Returns a complete row (list) of publication data for the given row number.

        For a JR1 report covering twelve months of usage data (typically Jan-Dec),
        there will be 22 columns of data in the row. The first item in the list
        will always be the given row number. Reports containing less (or more)
        months of usage data will have less or more list items, respectively.
        """

        datarow = list()
        datarow.append(row_num)
        for row in self._worksheet.iter_cols(min_row=row_num, min_col=1, max_row=row_num, max_col=22):
            for cell in row:
                datarow.append(cell.value)
        return datarow