import sqlite3
import settings
import os
import codecs
from util import userHandler

def create_table(conn):
    rec = False
    try:
        cursor = conn.cursor()
        cursor.execute('create table userlist (user_id INTEGER, item_id INTEGER, behavior_type INTEGER, user_geohash text, item_category INTEGER, time text)')
        cursor.execute('create table itemlist (item_id INTEGER, item_geohash text, item_category INTEGER)')
        conn.commit()
        rec = True
    except:
        pass
    cursor.close()
    return rec

def readfile(path):
    path = os.path.join(os.path.dirname(settings.__file__), path)
    if not os.path.isfile(path):
        raise ValueError('file path is invalid')
    with codecs.open(path, 'rb', 'utf-8') as fin:
        lines = [line.strip('\n') for line in fin.readlines()]
    lines = [tuple(line.split(',')) for line in lines[1:]]
    return lines

def insert_data(conn):
    cursor = conn.cursor()
    lines = readfile(settings.USER_FILE)
    print 'read user csv done'
    cursor.executemany('INSERT INTO userlist VALUES (?,?,?,?,?,?)', lines)
    print 'insert data to userlist done'
    lines = readfile(settings.ITEM_FILE)
    print 'read item csv done'
    cursor.executemany('INSERT INTO itemlist VALUES (?,?,?)', lines)
    print 'insert data to itemlist done'
    conn.commit()
    cursor.close()

def create_tran_data(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="traindata"')
        if cursor.fetchone():
            cursor.execute('drop table traindata')
            conn.commit()
        cursor.execute('select count(*) from userlist')
        total = cursor.fetchone()[0]
        require = int(total * 0.8)
        cursor.execute('create table traindata as select * from userlist order by userlist.time desc limit %s' % require)
        conn.commit()
        cursor.close()
    except:
        pass

def create_test_data(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="testdata"')
        if cursor.fetchone():
            cursor.execute('drop table testdata')
            conn.commit()
        cursor.execute('create table testdata (user_id INTEGER, item_id INTEGER)')
        conn.commit()
        lines = userHandler.get_user_data_set_by_time(-0.2)
        cursor.executemany('INSERT INTO testdata VALUES (?,?)', [[line['user_id'], line['item_id']] for line in lines if line['behavior_type'] == 4])
        conn.commit()
        cursor.close()
    except:
        pass


if __name__ == '__main__':
    try:
        db_path = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
        conn = sqlite3.connect(db_path)
        if create_table(conn):
            insert_data(conn)
        create_tran_data(conn)
        create_test_data(conn)
    except Exception as e:
        print e