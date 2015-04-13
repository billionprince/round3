import sqlite3
import settings
import os

DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
CONN = sqlite3.connect(DB_PATH)

def create_table(tableName, title, lines=None, drop=False):
    cursor = CONN.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % tableName)
    if cursor.fetchone() and drop:
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

def insert_line(tableName, line):
    cursor = CONN.cursor()
    q = 'INSERT INTO %s VALUES (%s)' % (tableName, ','.join([str(val) for val in line]))
    cursor.execute(q)
    CONN.commit()
    cursor.close()

def insert_lines(tableName, lines):
    cursor = CONN.cursor()
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

def table_exist(tableName):
    cursor = CONN.cursor()
    q = 'SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % tableName
    cursor.execute(q)
    return bool(cursor.fetchall())

def get_columns(tableName='userlist', fields=['user_id'], distinct=False):
    cursor = CONN.cursor()
    fields_str = ','.join(fields) if fields else '*'
    if distinct:
        q = 'select distinct %s from %s' % (fields_str, tableName)
    else:
        q = 'select %s from %s' % (fields_str, tableName)
    cursor.execute(q)
    lines = [line for line in cursor.fetchall()]
    cursor.close()
    return lines

def get_all_line_by_fields(tbName='userlist', dict={}, fields=[], distinct=False):
    cursor = CONN.cursor()
    if not distinct:
        q = 'select * from %s ' % tbName
    else:
        q = 'select distinct * from %s ' % tbName
    if fields:
        q.replace('*', ','.join(fields))
    if dict:
        q += 'where '
        para = []
        for k, v in dict.iteritems():
            if isinstance(v, list):
                para.append('%s in ("%s")' % (k, '""'.join(v)))
            else:
                para.append('%s="%s"' % (k, v))
        q += ' and '.join(para)
    cursor.execute(q)
    lines = [line for line in cursor.fetchall()]
    cursor.close()
    return lines
