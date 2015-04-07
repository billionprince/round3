import sqlite3
import settings
import os

DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
CONN = sqlite3.connect(DB_PATH)

def create_table(tableName, title, lines=None):
    cursor = CONN.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % tableName)
    if cursor.fetchone():
        cursor.execute('drop table %s' % tableName)
        CONN.commit()
    if not isinstance(title, list):
        raise ValueError('title should be list on dbhandler-create_table function')
    cursor.execute('create table %s (%s text)' % (tableName, ' text,'.join(title)))
    CONN.commit()
    if lines:
        cursor.executemany('INSERT INTO %s VALUES (%s)' % (tableName, ','.join(['?' for t in title])), lines)
        CONN.commit()
    cursor.close()

def delete_table(tableName):
    cursor = CONN.cursor()
    cursor.execute('drop table %s' % tableName)
    CONN.commit()
    cursor.close()

def read_table(tableName):
    cursor = CONN.cursor()
    cursor.execute('select * from %s' % tableName)
    lines = cursor.fetchall()
    rec = [line for line in lines]
    cursor.close()
    return rec
