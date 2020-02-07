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

    def __init__(self, workbook):
        self._workbook = openpyxl.load_workbook(filename=workbook, data_only=True)
        self._worksheet = self._workbook.active
        self._offset = self._get_offset()
        self._period = self._worksheet.cell(row=5+self._offset, column=1).value
        self._filename = os.path.basename(workbook)
    
    @property
    def filename(self):
        """
        Returns the Excel file name
        """
        
        return self._filename
    
    @property
    def platform(self):
        """
        Returns the platform name represented in cell C10
        """
        
        return self._worksheet.cell(row=10+self._offset, column=3).value

    @property
    def period(self):
        """
        Returns the report period represented in cell A5
        """
        
        return self._period
    
    @property
    def period_from(self):
        """
        Returns the period from date represented in cell A5
        """
        
        return datetime.strptime(self._period.strip()[:10], '%Y-%m-%d')

    @property
    def period_to(self):
        """
        Returns the period to date represented in cell A5
        """
        
        return datetime.strptime(self._period.strip()[-10:], '%Y-%m-%d')

    def data_range(self):
        """
        Returns the range of rows containing publication data.

        According to the COUNTER Code of Practice R4, publication data always
        starts at row 10 in the spreadsheet.
        """

        row_num = 10 + self._offset
        for row in self._worksheet.iter_rows(min_row=10+self._offset, min_col=1, max_row=1048576, max_col=1):
            if row[0].value == None:
                break
            row_num = row_num + 1
            
        return list(range(10+self._offset, row_num))
    
    def get_row(self, row_num):
        """
        Returns a complete row of publication data for the given row number.

        For a JR1 report covering twelve months of usage data (typically Jan-Dec),
        there will be 22 columns of data in the row. The first item in the list
        will always be the given row number. Reports containing less (or more)
        months of usage data will have less or more list items, respectively.
        """

        datarow = list()
        datarow.append(row_num)
        for row in self._worksheet.iter_cols(min_row=row_num, min_col=1, max_row=row_num, max_col=22):
            for cell in row:
                if cell.value != None: # Check for empty cells
                    datarow.append(str(cell.value).replace('"', ''))
                else:
                    datarow.append('')
        
        return datarow

    def _get_offset(self):
        """
        Returns the offset (if any) if the starting row is not 1.
        
        The COUNTER 4 standard requires that the JR1 report start at row 1 with
        the text 'Journal Report 1(R4)' in the first cell (A1). If the report begins
        on a subsequent row, the value of A1 will be different.
        """
        
        offset = 0
        if not str(self._worksheet.cell(row=1, column=1).value).startswith('Journal Report'):
            offset = 1
            while True:
                contents = str(self._worksheet.cell(row=1+offset, column=1).value)
                if contents.startswith('Journal Report'):
                    break
                else:
                    offset += 1
        
        return offset
