# -*- coding: utf-8 -*-
import sqlite3
import settings
import os

DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
CONN = sqlite3.connect(DB_PATH)
USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']
#包括浏览、收藏、加购物车、购买，对应取值分别是1、2、3、4


def get_user_data_set_by_time(percent):
    cursor = CONN.cursor()
    cursor.execute('select count(*) from userlist')
    total = cursor.fetchone()[0]
    if isinstance(percent, float):
        require = int(total * percent)
    else:
        raise ValueError('percent should be float type')
    cursor.execute('select * from userlist order by time limit %s' % require)
    lines = cursor.fetchall()
    rec = [{field: line[idx] for idx, field in enumerate(USERLIST)} for line in lines]
    cursor.close()
    return rec

def get_user_data_by_userid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select count(*) from userlist where user_id=%s' % int_uid)
    total_behavior_num = cursor.fetchone()[0]
    cursor.execute('select count(*) from userlist where user_id=%s and behavior_type=3' % int_uid)
    buy_behavior_num = cursor.fetchone()[0]
    rec = {uid: {'total_behavior_num': total_behavior_num, 'buy_behavior_num': buy_behavior_num}}
    cursor.close()
    return rec

def get_user_buy_item_by_userid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select distinct item_id from userlist where user_id=%s' % int_uid)
    lines = cursor.fetchall()
    rec = {uid: [str(line[0]) for line in lines]}
    cursor.close()
    return rec

def get_item_type_by_itemid(tid):
    cursor = CONN.cursor()
    int_tid = tid
    if not isinstance(tid, int):
        int_tid = int(int_tid)
    cursor.execute('select distinct item_category from itemlist where item_id=%s' % int_tid)
    line = cursor.fetchone()
    rec = {tid: str(line[0])}
    cursor.close()
    return rec

def get_item_by_item_type(item_type):
    cursor = CONN.cursor()
    if not isinstance(item_type, int):
        int_item_type = int(item_type)
    cursor.execute('select distinct item_id from itemlist where item_category=%s' % int_item_type)
    lines = cursor.fetchall()
    rec = {item_type: [str(line[0]) for line in lines]}
    cursor.close()
    return rec

if __name__ == '__main__':
    print get_item_by_item_type('7143')