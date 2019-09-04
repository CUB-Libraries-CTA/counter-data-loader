import mysql.connector
import config.config
import datetime
from datetime import date

class Counter:

    conn = mysql.connector.connect(**config.config.dbargs)

    def get_rowcount(self, table):
        rowcount = 0
        sql = u'SELECT MAX(id) FROM {0}'.format(table)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows[0][0] != None:
            rowcount = rows[0][0]
        return rowcount

class Platform(Counter):
    """
    Represents the platform table in the database.
    """

    def __init__(self):
        self._rowcount = Counter.get_rowcount(self, 'platform')

    def _next_id(self):
        self._rowcount += 1
        return self._rowcount
        
    def _is_duplicate(self, platform_name):
        isdupe = False
        sql = u'SELECT * FROM platform WHERE name = "{0}"'.format(platform_name)
        cursor = Counter.conn.cursor(buffered=True)
        cursor.execute(sql)
        if cursor.rowcount != 0:
            isdupe = True
        return isdupe
        
    def insert(self, platform_name):
        if not self._is_duplicate(platform_name):
            sql = u'INSERT INTO platform (id, name) VALUES ({0}, "{1}")' \
                .format(self._next_id(), platform_name)
            cursor = Counter.conn.cursor()
            cursor.execute(sql)
            Counter.conn.commit()

    def platform_id(self, platform_name):
        sql = u'SELECT id FROM platform WHERE name = "{0}"'.format(platform_name)
        cursor = Counter.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows[0][0]        

class Publisher(Counter):
    """
    Represents the publisher table in the database
    """

    def __init__(self):
        self._rowcount = Counter.get_rowcount(self, 'publisher')
        self._platform = Platform()
        self._platform_id = None
    
    def _next_id(self):
        self._rowcount += 1
        return self._rowcount

    def _is_duplicate(self, publisher_name, platform_id):
        isdupe = False
        sql = u'SELECT * FROM publisher WHERE name = "{0}" AND platform_id = {1}' \
            .format(publisher_name, platform_id)
        cursor = Counter.conn.cursor(buffered=True)
        cursor.execute(sql)
        if cursor.rowcount != 0:
            isdupe = True
        return isdupe

    def insert(self, datarow):

        publisher_name = datarow[2]
        platform_name = datarow[3]

        # Need to accommodate the case where no publisher is defined
        # for the data row being processed (blank cell in the spreadsheet)
        if not publisher_name:
            publisher_name = 'Not Defined'

        # Get platform_id for subsequent insert (this is the FK)
        if not self._platform_id:
            self._platform_id = self._platform.platform_id(platform_name)
        
        # Do the insert for unique items only
        if not self._is_duplicate(publisher_name, self._platform_id):
            sql = u'INSERT INTO publisher (id, name, platform_id) VALUES ({0}, "{1}", {2})' \
                .format(self._next_id(), publisher_name, self._platform_id)
            cursor = Counter.conn.cursor()
            cursor.execute(sql)
            Counter.conn.commit()

    def publisher_id(self, publisher_name, platform_id):
        if not publisher_name:
            publisher_name = 'Not Defined'
        sql = u'SELECT id FROM publisher WHERE name = "{0}" AND platform_id = {1}' \
            .format(publisher_name, platform_id)
        cursor = Counter.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows[0][0]

class Publication(Counter):
    """
    Represents the publisher table in the database
    """

    def __init__(self):
        self._rowcount = Counter.get_rowcount(self, 'publication')
        self._platform = Platform()
        self._publisher = Publisher()
        self._platform_id = None
        self._publisher_id = None
    
    def _next_id(self):
        self._rowcount += 1
        return self._rowcount

    def _is_duplicate(self, publication_title, publisher_id):
        isdupe = False
        sql = u'SELECT * FROM publication WHERE title = "{0}" AND publisher_id = {1}' \
            .format(publication_title, publisher_id)
        cursor = Counter.conn.cursor(buffered=True)
        cursor.execute(sql)
        if cursor.rowcount != 0:
            isdupe = True
        return isdupe

    def insert(self, datarow):

        journal_title = datarow[1]
        publisher_name = datarow[2]
        platform_name = datarow[3]
        journal_doi = datarow[4]
        proprietary_id = datarow[5]
        print_issn = datarow[6]
        online_issn = datarow[7]

        # Get publisher ID for publisher name
        if not self._platform_id:
            self._platform_id = self._platform.platform_id(platform_name)
        self._publisher_id = self._publisher.publisher_id(publisher_name, self._platform_id)

        # Insert unique publications
        if not self._is_duplicate(journal_title, self._publisher_id):
            sql = u'INSERT INTO publication (id, publisher_id, title, print_issn, online_issn, journal_doi, proprietary_id) \
                VALUES ({0}, {1}, "{2}", "{3}", "{4}", "{5}", "{6}")'.format(self._next_id(), self._publisher_id, \
                journal_title, print_issn, online_issn, journal_doi, proprietary_id)
            cursor = Counter.conn.cursor()
            cursor.execute(sql)
            Counter.conn.commit()
