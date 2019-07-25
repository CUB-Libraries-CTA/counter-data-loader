import mysql.connector
import config.config
import datetime
from datetime import date

class Platform:
    """
    Represents the platform table in the database.

    The only published class method is insert() to facilitate adding rows
    to the table. The table contains only unique records.
    """

    def __init__(self):
        self._conn = mysql.connector.connect(**config.config.dbargs)
        self._rowcount = self._get_rowcount()

    def _get_rowcount(self):
        rowcount = 0
        sql = u"""SELECT MAX(id) FROM platform"""
        cursor = self._conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows[0][0] != None:
            rowcount = rows[0][0]
        return rowcount
    
    def _get_id(self):
        self._rowcount += 1
        return self._rowcount
        
    def _is_duplicate(self, platform):
        isdupe = False
        sql = u"""SELECT * FROM platform WHERE name = %(name)s"""
        params = {'name': platform}
        cursor = self._conn.cursor(buffered=True)
        cursor.execute(sql, params)
        if cursor.rowcount != 0:
            isdupe = True
        return isdupe
        
    def insert(self, platform):
        if not self._is_duplicate(platform):
            sql = u"""INSERT INTO platform (id, name) VALUES (%(id)s, %(name)s)"""
            params = {'id': self._get_id(), 'name': platform}
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            self._conn.commit()
