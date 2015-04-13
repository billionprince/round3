import sqlite3
import settings
import os
import codecs
from util import userHandler

TRAIN_DATA_PERCENT = 0.9
USERLIST_WITHOUT_NOISY_TABLE_NAME = 'userlistwithoutnoisy'
TRAIN_DELETE_NOISY_DATA = 'traindeletenoisydata'


def create_table(conn):
    rec = False
    try:
        cursor = conn.cursor()
        cursor.execute(
            'create table userlist (user_id INTEGER, item_id INTEGER, behavior_type INTEGER, user_geohash text, item_category INTEGER, time text)')
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


def create_tran_data(conn, line_num, tableName='userlist'):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="traindata"')
        if cursor.fetchone():
            cursor.execute('drop table traindata')
            conn.commit()
        cursor.execute(
            'create table traindata as select * from %s order by time asc limit %s' % (tableName, line_num))
        conn.commit()
    except Exception as e:
        print e
        pass
    cursor.close()


def create_test_data(conn, line_num, tableName='userlist'):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="testdata"')
        if cursor.fetchone():
            cursor.execute('drop table testdata')
            conn.commit()
        q = 'create table testdata as '
        q += 'select user_id, item_id from '
        q += '(select user_id, item_id, behavior_type '
        q += 'from %s order by time desc limit %s) ' % (tableName, line_num)
        q += 'where behavior_type=4'
        cursor.execute(q)
        conn.commit()
    except Exception as e:
        print e
        pass
    cursor.close()


def divide_data_set(conn, tableName='userlist'):
    cursor = conn.cursor()
    cursor.execute('select count(*) from %s' % tableName)
    total = cursor.fetchone()[0]
    cursor.close()
    tran_line_num = int(total * TRAIN_DATA_PERCENT)
    test_line_num = total - tran_line_num
    create_tran_data(conn, tran_line_num, tableName)
    create_test_data(conn, test_line_num, tableName)

def delete_noisy_data(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % USERLIST_WITHOUT_NOISY_TABLE_NAME)
        if cursor.fetchone():
            cursor.execute('drop table "%s"' % USERLIST_WITHOUT_NOISY_TABLE_NAME)
            conn.commit()
        str = 'create table %s ' % USERLIST_WITHOUT_NOISY_TABLE_NAME
        str += 'as select user_id, item_id, behavior_type, '
        str += 'min(user_geohash) as user_geohash, min(item_category) as item_category, time '
        str += 'from userlist where time not like "%2014-12-12%" '
        str += 'group by user_id, item_id, behavior_type, time'
        cursor.execute(str)
        conn.commit()
    except Exception as e:
        print e
        pass
    cursor.close()

# def create_user_buy_train_delete_noisy_data():
#     cursor = conn.cursor()
#     try:
#         q = 'SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % TRAIN_DELETE_NOISY_DATA
#         cursor.execute(q)
#         if cursor.fetchone():
#             cursor.execute('drop table %s' % TRAIN_DELETE_NOISY_DATA)
#             conn.commit()
#         q = 'create table %s as ' % TRAIN_DELETE_NOISY_DATA
#         q += 'select user_id, item_id, behavior_type, '
#         q += 'item_category, min(time) as time, count(*) as num '
#         q += 'from traindata '
#         q += 'group by user_id, item_id, behavior_type'
#         cursor.execute(q)
#         conn.commit()
#         q = 'insert into %s ' % TRAIN_DELETE_NOISY_DATA
#         q += 'select user_id, item_id, behavior_type, item_category, time, "" '
#         q += 'from traindata where behavior_type=4'
#         cursor.execute(q)
#         conn.commit()
#     except Exception as e:
#         print e
#         pass
#     cursor.close()

# def create_user_buy_train_data(conn):
#     cursor = conn.cursor()
#     try:
#         cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="trainbuydata"')
#         if cursor.fetchone():
#             cursor.execute('drop table trainbuydata')
#             conn.commit()
#         cursor.execute('create table trainbuydata as select * from traindata where behavior_type=4')
#         conn.commit()
#     except Exception as e:
#         print e
#         pass
#     cursor.close()

if __name__ == '__main__':
    try:
        db_path = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
        conn = sqlite3.connect(db_path)
        if create_table(conn):
            insert_data(conn)
        delete_noisy_data(conn)
        divide_data_set(conn, USERLIST_WITHOUT_NOISY_TABLE_NAME)
        # create_user_buy_train_data(conn)
        # create_user_buy_train_delete_noisy_data()
    except Exception as e:
        print e