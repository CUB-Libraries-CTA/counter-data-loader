import mysql.connector
import dataloader.config
import html
import datetime
from datetime import datetime

class CounterDb:
    """
    The parent class for the COUNTER database. It provides a common
    connection object for child tables. This class is never instantiated
    on its own.
    """

    conn = mysql.connector.connect(**dataloader.config.dbargs)

class TitleReportTable(CounterDb):
    """
    Represents the title_report table.
    """

    def __init__(self):
        pass

    def _is_duplicate(self, row):
        """
        This is a check to determine if the title (journal or book) is
        already in the table. A title is a duplicate if the following
        data elements are the same:

          - title
          - publisher
          - platform

        Note that there may be instances where a book or journal title
        may appear to be unique but in fact is not. For example, the
        publisher ACM may also appear as Association for Computing Machinery.
        In this case, the title will be considered different and consequently
        a new row will be inserted in the table. However, this has no impact
        on determining usage for a specific title as both records will
        be combined to provide a total usage when filtering by title alone.

        Returns the cursor fetch result, which will be None or a 1-element tuple
        containing the id of the duplicate row.
        """

        platform = PlatformTable()
        params = (row.title, row.publisher, platform.get_platform_id(row.platform))
        sql = u"SELECT id FROM title_report WHERE \
            title = %s AND \
            publisher = %s AND \
            platform_id = %s"
        cursor = CounterDb.conn.cursor(named_tuple=True, buffered=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return row
    
    def _set_publisher(self, publisher):
        """
        Sets the publisher name to Not Defined in select cases. HTML
        entities are also unescaped in the publisher name.
        """

        if publisher is None or '???' in publisher or publisher == '':
            return 'Not Defined'
        else:
            return html.unescape(html.unescape(publisher))
    
    def _set_title(self, title):
        """
        Unescapes HTML entities in the title name.
        """

        return html.unescape(html.unescape(title))

    def insert(self, row, run_date):
        """
        Inserts a row in the title_report table. Returns the id
        of the inserted row.
        """

        # If the title/publisher/platform combination already exists in this
        # table, then we only need the rowid to insert metric data.
        dupe = self._is_duplicate(row)
        if dupe:
            rowid = dupe.id
        
        # If the row is not a duplicate, then proceed with assigning parameter
        # values, which depends on whether this is R4 or R5 data.
        else:

            # Do the insert and return the resultant row ID.
            sql = u"INSERT INTO title_report SET \
                id = NULL, \
                title = %s, \
                title_type = %s, \
                publisher = %s, \
                publisher_id = %s, \
                platform_id = %s, \
                doi = %s, \
                proprietary_id = %s, \
                isbn = %s, \
                print_issn = %s, \
                online_issn = %s, \
                uri = %s, \
                yop = %s, \
                create_date = %s, \
                update_date = %s"

            # Build the SQL parameter list and execute.
            platform = PlatformTable()
            platform_id = platform.get_platform_id(row.platform)
            publisher = self._set_publisher(row.publisher)
            title = self._set_title(row.title)
            create_date = datetime.fromisoformat(run_date.replace('Z','+06:00'))
            params = (title, row.title_type, publisher, row.publisher_id,
                platform_id, row.doi, row.proprietary_id, row.isbn, row.print_issn,
                row.online_issn, row.uri, row.yop, create_date, create_date)
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            rowid = cursor.lastrowid
            CounterDb.conn.commit()

        return rowid

class MetricTable(CounterDb):
    """
    Represents the metric table.
    """

    ACCESS_TYPE = ['', 'Controlled', 'OA_Gold', 'Other_Free_To_Read']
    METRIC_TYPE = ['', 'Total_Item_Investigations', 'Total_Item_Requests',
        'Unique_Item_Investigations', 'Unique_Item_Requests',
        'Unique_Title_Investigations', 'Unique_Title_Requests',
        'Limit_Exceeded', 'No_License']

    PERIODS = ['', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
        'sep', 'oct', 'nov', 'dec']

    def __init__(self):
        pass

    def _is_duplicate(self, title_report_id, access_type, metric_type, period):
        """
        Checks for duplicate rows for the given title report id.

        Returns the cursor fetch result, which will be None or a 1-element tuple
        containing the id of the duplicate row.
        """

        sql = u"SELECT id FROM metric \
            WHERE title_report_id = %s \
            AND access_type = %s \
            AND metric_type = %s \
            AND period = %s"
        params = (title_report_id, access_type, metric_type, period)
        cursor = CounterDb.conn.cursor(named_tuple=True, buffered=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return row

    def insert(self, row, rowid, begin_date, end_date, run_date):
        """
        Inserts a row in the metric table. The row to insert must
        have a corresponding title entry (journal or book).
        """
        
        # Build date and period information needed for each row
        report_begin = datetime.fromisoformat(begin_date)
        report_end = datetime.fromisoformat(end_date)
        create_date = datetime.fromisoformat(run_date.replace('Z','+06:00'))
        
        # A row will be inserted for each month column in the source
        # spreadsheet. The actual number of months is determined from
        # the start and end dates contained in the report header.
        for i in range(report_begin.month, report_end.month + 1):
            ndx = row._fields.index(self.PERIODS[i])
            period = datetime(report_begin.year, i, 1).strftime('%Y-%m-%d')
            period_total = int(float(row[ndx])) # float conversion deals with cases of '0.0'

            # Is this an update or an insert?
            dupe = self._is_duplicate(rowid, row.access_type, row.metric_type, period)
            if dupe:
                sql = u"UPDATE metric SET \
                    period_total = %s, \
                    update_date = NOW() \
                    WHERE id = %s"
                params = (period_total, dupe.id)
            else:
                sql = u"INSERT INTO metric SET \
                    id = NULL, \
                    title_report_id = %s, \
                    access_type = %s, \
                    metric_type = %s, \
                    period = %s, \
                    period_total = %s, \
                    create_date = %s, \
                    update_date = %s"
                params = (rowid, self.ACCESS_TYPE.index(row.access_type),
                    self.METRIC_TYPE.index(row.metric_type), period, period_total,
                    create_date, create_date)

            # Do the insert and return.
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            CounterDb.conn.commit()

class PlatformTable(CounterDb):
    """
    Represents the platform_ref table.
    """

    def __init__(self):
        pass

    def get_platform_id(self, name):
        """
        Returns the corresponding ID for a given platform name. If the
        platform name is found, the ID will be returned; otherwise,
        the return value will be None.
        """

        params = (name,)
        sql = u"SELECT id FROM platform_ref WHERE name = %s"
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return row[0]

class ReportInventoryTable(CounterDb):
    """
    Represents the spreadsheet inventory table.
    """

    def __init__(self):
        pass

    def is_loaded(self, report):
        """
        Checks to see if the report has already been loaded.
        """

        sql = u"SELECT platform, begin_date, end_date \
            FROM report_inventory \
            WHERE platform = %s \
            AND begin_date = %s \
            AND end_date = %s \
            AND row_cnt = %s"
        params = (report.platform, report.begin_date, report.end_date, report.row_count)
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return (row is not None)

    def insert(self, report):
        """
        Inserts the report details into the inventory table.
        """
        
        sql = u"INSERT INTO report_inventory SET \
            id = NULL, \
            excel_name = %s, \
            platform = %s, \
            begin_date = %s, \
            end_date = %s, \
            row_cnt = %s, \
            load_date = NOW()"
        params = (report.filename, report.platform, report.begin_date,
            report.end_date, len(report.data_rows()))
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql, params)
        CounterDb.conn.commit()
