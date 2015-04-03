import sqlite3
import settings
import os
import codecs

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('create table userlist (user_id INTEGER, item_id INTEGER, behavior_type INTEGER, user_geohash text, item_category INTEGER, time text)')
    cursor.execute('create table itemlist (item_id INTEGER, item_geohash text, item_category INTEGER)')
    conn.commit()
    cursor.close()

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


if __name__ == '__main__':
    try:
        db_path = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
        conn = sqlite3.connect(db_path)
        create_table(conn)
        insert_data(conn)
    except Exception as e:
        print e