import mysql.connector
import dataloader.config
import collections
import datetime
from datetime import date

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
        """

        platform = PlatformTable()
        params = (row.title, row.publisher, platform.get_platform_id(row.platform),
            row.doi, row.proprietary_id)
        sql = u"SELECT id FROM title_report WHERE \
            title = %s AND \
            publisher = %s AND \
            platform_id = %s AND \
            (doi = %s OR doi IS NULL) AND \
            (proprietary_id = %s OR proprietary_id IS NULL)"
        cursor = CounterDb.conn.cursor(named_tuple=True, buffered=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()
        cursor.close()

        return (row is not None), row

    def insert(self, row):
        """
        Inserts a row in the title_report table.
        """

        isdupe, rowid = self._is_duplicate(row)
        if isdupe:
            rowid = rowid.id
        else:
            platform = PlatformTable()
            if row.report_id.startswith('TR'):
                isbn, yop = None, None
                if 'isbn' in row._fields:
                    isbn = row.isbn
                if 'yop' in row._fields:
                    yop = row.yop
                params = (row.title, row.title_type, row.publisher, row.publisher_id,
                    platform.get_platform_id(row.platform), row.doi,
                    row.proprietary_id, isbn, row.print_issn, row.online_issn,
                    row.uri, yop, None)
            else:
                params = (row.title, row.title_type, row.publisher, None,
                    platform.get_platform_id(row.platform), row.doi,
                    row.proprietary_id, None, row.print_issn, row.online_issn,
                    None, None, None)

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
                status = %s"
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            rowid = cursor.lastrowid
            CounterDb.conn.commit()
            cursor.close()

        return rowid

class MetricTable(CounterDb):
    """
    Represents the metric table.
    """

    CONTROLLED = 1
    TOTAL_ITEM_REQUESTS = 2

    ACCESS_TYPE = ['', 'Controlled', 'OA_Gold', 'Other_Free_To_Read']
    METRIC_TYPE = ['', 'Total_Item_Investigations', 'Total_Item_Requests',
        'Unique_Item_Investigations', 'Unique_Item_Requests',
        'Unique_Title_Investigations', 'Unique_Title_Requests',
        'Limit_Exceeded', 'No_License']

    def __init__(self):
        pass

    def insert(self, row, begin_date, end_date, rowid):
        """
        Inserts a row in the metric table. The row to insert must
        have a corresponding title entry (journal or book).
        """
        begin = date.fromisoformat(begin_date)
        end = date.fromisoformat(end_date)
        periods = ['', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for m in range(begin.month, end.month + 1):
            idx = row._fields.index(periods[m])
            period = datetime.date(begin.year, m, 1).strftime('%Y-%m-%d')
            period_total = int(row[idx])

            if row.report_id.startswith('TR'):
                params = (rowid, self.ACCESS_TYPE.index(row.access_type),
                    self.METRIC_TYPE.index(row.metric_type),
                    period, period_total)
            else:
                params = (rowid, self.CONTROLLED, self.TOTAL_ITEM_REQUESTS,
                    period, period_total)
            sql = u"INSERT INTO metric SET \
                id = NULL, \
                title_report_id = %s, \
                access_type = %s, \
                metric_type = %s, \
                period = %s, \
                period_total = %s"
            cursor = CounterDb.conn.cursor()
            cursor.execute(sql, params)
            CounterDb.conn.commit()
            cursor.close()

class PlatformTable(CounterDb):
    """
    Represents the platform_ref table.
    """

    def __init__(self):
        pass

    def get_platform_id(self, name):
        """
        Gets the corresponding ID for a given platform name. Both the name
        and alias columns need to be checked. If the platform name is found,
        the ID will be returned; otherwise, the return value will be None.
        """

        params = (name,)
        sql = u"SELECT id FROM platform_ref WHERE name = %s"
        cursor = CounterDb.conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return row[0]
