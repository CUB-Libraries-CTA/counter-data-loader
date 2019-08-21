import mysql.connector
import config.config
import datetime
from datetime import date

class Counter:

    conn = mysql.connector.connect(**config.config.dbargs)

    def get_rowcount(self, table):
        rowcount = 0
        sql = 'SELECT MAX(id) FROM ' + table
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
        sql = u'SELECT * FROM platform WHERE name = %(name)s'
        params = {'name': platform_name}
        cursor = Counter.conn.cursor(buffered=True)
        cursor.execute(sql, params)
        if cursor.rowcount != 0:
            isdupe = True
        return isdupe
        
    def insert(self, platform_name):
        if not self._is_duplicate(platform_name):
            sql = u'INSERT INTO platform (id, name) VALUES (%(id)s, %(name)s)'
            params = {'id': self._next_id(), 'name': platform_name}
            cursor = Counter.conn.cursor()
            cursor.execute(sql, params)
            Counter.conn.commit()

    def platform_id(self, platform_name):
        sql = u'SELECT id FROM platform WHERE name = %(name)s'
        params = {'name': platform_name}
        cursor = Counter.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows[0][0]        

class Publisher(Counter):
    """
    Represents the publisher table in the database
    """

    def __init__(self):
        self._rowcount = Counter.get_rowcount(self, 'publisher')
        self._platform = Platform()
    
    def _next_id(self):
        self._rowcount += 1
        return self._rowcount

    def _is_duplicate(self, publisher_name, platform_id):
        isdupe = False
        sql = u'SELECT * FROM publisher WHERE name = %(name)s AND platform_id = %(platform_id)s'
        params = {'name': publisher_name, 'platform_id': platform_id}
        cursor = Counter.conn.cursor(buffered=True)
        cursor.execute(sql, params)
        if cursor.rowcount != 0:
            isdupe = True
        return isdupe

    def insert(self, datarow):
        
        # Need to accommodate the case where no publisher is defined
        # for the data row being processed
        datarow[2] = datarow[2].strip()
        if not datarow[2]:
            datarow[2] = 'Not Defined'
        
        # Do the insert for unique items
        platform_id = self._platform.platform_id(datarow[3])
        if not self._is_duplicate(datarow[2], platform_id):
            sql = u'INSERT INTO publisher (id, name, platform_id) VALUES (%(id)s, %(name)s, %(platform_id)s)'
            params = {'id': self._next_id(), 'name': datarow[2], 'platform_id': platform_id}
            cursor = Counter.conn.cursor()
            cursor.execute(sql, params)
            Counter.conn.commit()
