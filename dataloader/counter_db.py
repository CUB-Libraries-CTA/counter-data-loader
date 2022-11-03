from collections import namedtuple
import mysql.connector
import dataloader.config
import html
import subprocess, os, sys
import datetime
from datetime import datetime

class CounterDb:
    """
    The parent class for the COUNTER database. It provides a common
    connection object for table classes. This class is never instantiated
    on its own.
    """
    ACCESS_TYPE = ['', 'Controlled', 'OA_Gold', 'Other_Free_To_Read']
    METRIC_TYPE = ['', 'Total_Item_Investigations', 'Total_Item_Requests',
        'Unique_Item_Investigations', 'Unique_Item_Requests',
        'Unique_Title_Investigations', 'Unique_Title_Requests',
        'Limit_Exceeded', 'No_License']

    PERIODS = ['', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
        'sep', 'oct', 'nov', 'dec']

    conn = mysql.connector.connect(**dataloader.config.dbargs, buffered=True)

class BulkImport(CounterDb):
    """
    Performs a bulk import of title and metric text files.
    """
    def __init__(self, reportdir):
        self._reportdir = reportdir

    def import_all(self):
        # Truncate database temp tables first.
        cursor = CounterDb.conn.cursor()
        cursor.execute('TRUNCATE TABLE title_report_temp')
        cursor.execute('TRUNCATE TABLE metric_temp')

        # Build the mysqlimport command line and then execute.
        user = dataloader.config.dbargs['user']
        passwd = dataloader.config.dbargs['password']
        database = dataloader.config.dbargs['database']
        cmd = 'mysqlimport --user={0} --password={1} --delete {2} {3}/title_report_temp \
             {3}/metric_temp > mysqlimport_out.txt'.format(user, passwd, database, self._reportdir)
        print(cmd)
        try:
            if os.system(cmd) != 0:
                raise OSError # Consider using a custom exception class for this purpose.
            os.remove('mysqlimport_out.txt')
            
            # The following code uses the subprocess module to run the same command
            # but with more options to control execution. The above approach though is
            # wholly acceptable and is simpler.

            #sp = subprocess.run(args=[
            #    "mysqlimport",
            #    "--delete",
            #    "counter5",
            #    "reports/title_report_temp",
            #    "reports/metric_temp"],
            #    stdout=subprocess.DEVNULL,
            #    shell=True,
            #    check=True)
            #sp.check_returncode()

        except OSError:
            print('There was a problem importing records')

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
          - isbn
          - yop

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
        params = (row.title, row.publisher, platform.get_platform_id(row.platform),
            row.isbn, row.yop)
        sql = u"SELECT id FROM title_report WHERE \
            title = %s AND \
            publisher = %s AND \
            platform_id = %s AND \
            isbn = %s AND \
            yop = %s"
        cursor = CounterDb.conn.cursor(named_tuple=True)
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

    def insert(self, row):
        """
        Inserts a row in the title_report table. Returns the id
        of the inserted row.

        DEPRECATED when using bulk import method.
        """
        # If the title/publisher/platform combination already exists in this
        # table, then we only need the rowid to insert metric data.
        dupe = self._is_duplicate_mem(row)
        if dupe:
            rowid = dupe

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
                yop = %s"

            # Build the SQL parameter list and execute.
            platform = PlatformTable()
            platform_id = platform.get_platform_id(row.platform)
            publisher = self._set_publisher(row.publisher)
            title = self._set_title(row.title)
            params = (title, row.title_type, publisher, row.publisher_id,
                platform_id, row.doi, row.proprietary_id, row.isbn, row.print_issn,
                row.online_issn, row.uri, row.yop)
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            rowid = cursor.lastrowid
            CounterDb.conn.commit()

        return rowid

    def insert_from_temp(self):
        """
        Inserts rows from title temp table into the title_report table.
        """
        # For every row in the title_report_temp table, either do an insert
        # or, if a duplicate row, update the title_report_id reference
        # in the temp table. Regardless of insert or update, the title_report_id
        # will need to be updated.
        cursor = CounterDb.conn.cursor(named_tuple=True)
        cursor.execute('SELECT * FROM title_report_temp')
        rows = cursor.fetchall()
        for row in rows:
            # Check for duplicate.
            dupe = self._is_duplicate(row)
            if dupe:
                rowid = dupe.id
            else:
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
                    yop = %s"
                platform = PlatformTable()
                platform_id = platform.get_platform_id(row.platform)
                publisher = self._set_publisher(row.publisher)
                title = self._set_title(row.title)
                params = (title, row.title_type, publisher, row.publisher_id,
                    platform_id, row.doi, row.proprietary_id, row.isbn, row.print_issn,
                    row.online_issn, row.uri, row.yop)
                cursor = CounterDb.conn.cursor()
                cursor.execute(sql, params)
                rowid = cursor.lastrowid
                CounterDb.conn.commit()
            
            # Update title_report_id in temp table
            sql = u"UPDATE title_report_temp SET title_report_id = %s WHERE id = %s"
            params = (rowid, row.id)
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            CounterDb.conn.commit()

class MetricTable(CounterDb):
    """
    Represents the metric table.
    """
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
        cursor = CounterDb.conn.cursor(named_tuple=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return row

    def insert(self, row, rowid, begin_date, end_date):
        """
        Inserts a row in the metric table. The row to insert must
        have a corresponding title entry (journal or book).

        DEPRECATED when using bulk import method.
        """
        # Build date and period information needed for each row
        report_begin = datetime.fromisoformat(begin_date)
        report_end = datetime.fromisoformat(end_date)
        
        # A row will be inserted for each month column in the source
        # spreadsheet. The actual number of months is determined from
        # the start and end dates contained in the report header.
        for i in range(report_begin.month, report_end.month + 1):
            ndx = row._fields.index(self.PERIODS[i])
            period = datetime(report_begin.year, i, 1).strftime('%Y-%m-%d')
            period_total = int(float(row[ndx])) # float conversion deals with cases of '0.0'

            # In some cases, access type may be blank. These are coded as "Not Defined".
            access_type = row.access_type
            if len(access_type) == 0:
                access_type = 'Not Defined'

            # Is this an update or an insert?
            dupe = self._is_duplicate(rowid, access_type, row.metric_type, period)
            if dupe:
                sql = u"UPDATE metric SET \
                    period_total = %s \
                    WHERE id = %s"
                params = (period_total, dupe.id)
            else:
                sql = u"INSERT INTO metric SET \
                    id = NULL, \
                    title_report_id = %s, \
                    access_type = %s, \
                    metric_type = %s, \
                    period = %s, \
                    period_total = %s"
                params = (rowid, self.ACCESS_TYPE.index(access_type),
                    self.METRIC_TYPE.index(row.metric_type), period, period_total)

            # Do the insert and return.
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            CounterDb.conn.commit()

    def insert_from_temp(self):
        """
        Inserts data from the metric temp table in the main metric table.
        """
        # First step is to update the title_report_id in the temp table.
        # Basic algorithm:
        # - for every row in the temp table, update the title_report_id
        # - where the report filename and row number are the same
        sql = u"UPDATE metric_temp m SET m.title_report_id = \
            (SELECT t.title_report_id FROM title_report_temp t WHERE \
            t.excel_name = m.excel_name AND t.row_num = m.row_num)"
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql)
        CounterDb.conn.commit()

        # Next, do the inserts into the main metric table but check for
        # duplicates first.
        cursor = CounterDb.conn.cursor(named_tuple=True)
        cursor.execute('SELECT * FROM metric_temp')
        rows = cursor.fetchall()
        for row in rows:
            dupe = self._is_duplicate(row.title_report_id, row.access_type, row.metric_type, row.period)
            if dupe:
                sql = u"UPDATE metric SET \
                    period_total = %s \
                    WHERE id = %s"
                params = (row.period_total, dupe.id)
            else:
                sql = u"INSERT INTO metric SET \
                    id = NULL, \
                    title_report_id = %s, \
                    title_type = %s, \
                    access_type = %s, \
                    metric_type = %s, \
                    period = %s, \
                    period_total = %s"
                params = (row.title_report_id, row.title_type, row.access_type, row.metric_type,
                    row.period, row.period_total)

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
        sql = u"SELECT platform, run_date, begin_date, end_date \
            FROM report_inventory \
            WHERE platform = %s \
            AND run_date = %s \
            AND begin_date = %s \
            AND end_date = %s \
            AND row_cnt = %s"
        params = (report.platform, report.run_date, report.begin_date,
            report.end_date, report.row_count)
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return (row is not None)

    def insert(self, report, load_start, load_end):
        """
        Inserts the report details into the inventory table.
        """
        sql = u"INSERT INTO report_inventory SET \
            id = NULL, \
            excel_name = %s, \
            platform = %s, \
            run_date = %s, \
            begin_date = %s, \
            end_date = %s, \
            row_cnt = %s, \
            load_start = %s, \
            load_end = %s, \
            load_date = CURRENT_DATE"
        params = (report.filename, report.platform, report.run_date, report.begin_date,
            report.end_date, len(report.data_rows()), load_start, load_end)
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql, params)
        CounterDb.conn.commit()
