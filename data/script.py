import sqlite3
import settings
import os
import codecs
from util import userHandler

TRAIN_DATA_PERCENT = 0.9

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

def create_tran_data(conn, line_num):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="traindata"')
        if cursor.fetchone():
            cursor.execute('drop table traindata')
            conn.commit()
        cursor.execute('create table traindata as select * from userlist order by userlist.time asc limit %s' % line_num)
        conn.commit()
    except Exception as e:
        print e
        pass
    cursor.close()

def create_test_data(conn, line_num):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="testdata"')
        if cursor.fetchone():
            cursor.execute('drop table testdata')
            conn.commit()
        cursor.execute('create table testdata as select user_id, item_id from userlist where behavior_type=4 order by userlist.time desc limit %s' % line_num)
        conn.commit()
    except Exception as e:
        print e
        pass
    cursor.close()

def create_user_buy_train_data(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="trainbuydata"') #trainbuydata
        if cursor.fetchone():
            cursor.execute('drop table trainbuydata')
            conn.commit()
        cursor.execute('create table trainbuydata as select * from traindata where behavior_type=4')
        conn.commit()
    except Exception as e:
        print e
        pass
    cursor.close()


if __name__ == '__main__':
    try:
        db_path = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
        conn = sqlite3.connect(db_path)
        if create_table(conn):
            insert_data(conn)
        cursor = conn.cursor()
        cursor.execute('select count(*) from userlist')
        total = cursor.fetchone()[0]
        cursor.close()
        tran_line_num = int(total * TRAIN_DATA_PERCENT)
        test_line_num = total - tran_line_num
        # create_tran_data(conn, tran_line_num)
        # create_test_data(conn, test_line_num)
        create_user_buy_train_data(conn)
    except Exception as e:
        print e