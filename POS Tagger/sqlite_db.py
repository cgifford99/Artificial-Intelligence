import os
import sqlite3


class SQLite3_DB:
    def __init__(self, db_filename):
        self.db_filename = os.path.abspath(db_filename)
        try:
            self.conn = sqlite3.connect(self.db_filename)
        except Exception as ex:
            raise Exception('ERROR: Failed to connect to database at: ' + self.db_filename)

    def executeUpdateQuery(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            self.conn.commit()
        except sqlite3.Error as error:
            raise Exception('ERROR: Failed to execute query: ' + str(error))

    def executeUpdateManyQuery(self, query, tuple_arr):
        try:
            self.conn.executemany(query, tuple_arr)
            self.conn.commit()
        except sqlite3.Error as error:
            raise Exception('ERROR: Failed to execute query: ' + str(error))

    def executeRetrievalQuery(self, query):
        results = []
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            results = cur.fetchall()
        except sqlite3.Error as error:
            raise Exception('ERROR: Failed to execute query: ' + str(error))

        return results
