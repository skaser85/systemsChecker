"""
Simple sqlite3 wrapper
"""

from pyodbc import Connection, Cursor, connect
from dataclasses import dataclass, field

@dataclass
class Database:
    """ Simple SQL Server wrapper """
    server: str
    name: str
    connection: Connection = field(init=False)
    cursor: Cursor = field(init=False)

    def __post_init__(self):
        self.connection = connect('Driver={SQL Server};'
                            f'Server={self.server};'
                            f'Database={self.name};'
                            'Trusted_Connection=yes;')
        self.cursor = self.connection.cursor()

    def select(self, sql: str, values: tuple[str] = ()) -> Cursor:
        """ Select records from a table """
        return self._execute_(sql, values)

    def insert(self, sql: str, values: tuple[str] = ()) -> Cursor:
        """ Insert a record into a table """
        self._execute_(sql, values)
        self.cursor.commit()
        return self.cursor

    def update(self, sql: str, values: tuple[str] = ()) -> Cursor:
        """ Update a value on a record in a table """
        self._execute_(sql, values)
        self.cursor.commit()
        return self.cursor

    def delete(self, sql: str, values: tuple[str] = ()) -> Cursor:
        """ Delete a record from the table """
        self._execute_(sql, values)
        self.cursor.commit()
        return self.cursor

    def _execute_(self, sql: str, values: tuple[str] = ()) -> Cursor:
        """ Execute a sql query """
        self.cursor.execute(sql, values)
        return self.cursor

if __name__ == '__main__':
    ...