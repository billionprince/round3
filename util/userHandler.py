# -*- coding: utf-8 -*-
import sqlite3
import settings
import os

DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
CONN = sqlite3.connect(DB_PATH)
USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']
#包括浏览、收藏、加购物车、购买，对应取值分别是1、2、3、4

def get_all_uid():
    cursor = CONN.cursor()
    cursor.execute('select distinct user_id from userlist')
    lines = cursor.fetchall()
    rec = [line[0] for line in lines]
    cursor.close()
    return rec

def get_user_data_set_by_time(percent):
    cursor = CONN.cursor()
    cursor.execute('select count(*) from userlist')
    total = cursor.fetchone()[0]
    if isinstance(percent, float):
        require = int(total * percent)
    else:
        raise ValueError('percent should be float type')
    str = 'select * from userlist '
    if percent < 0:
        str += 'order by time desc '
    else:
        str += 'order by time asc '
    str += 'limit %s' % abs(require)
    cursor.execute(str)
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

def get_user_buy_items_by_userid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select distinct item_id from userlist where user_id=%s and behavior_type=4' % int_uid)
    lines = cursor.fetchall()
    rec = [str(line[0]) for line in lines]
    cursor.close()
    return rec

def get_user_buy_items_and_buytimes_by_userid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select item_id, count(*) from userlist where user_id=%s and behavior_type=4 group by item_id' % int_uid)
    lines = cursor.fetchall()
    rec = {uid: [(str(line[0]), int(line[1])) for line in lines]}
    cursor.close()
    return rec

def get_items_on_shopping_cart_by_uid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select distinct item_id from userlist where user_id=%s and behavior_type=3' % int_uid)
    lines = cursor.fetchall()
    rec = {uid: [str(line[0]) for line in lines]}
    cursor.close()
    return rec

def get_buy_items_of_mulitple_users_by_userid(uidlist):
    cursor = CONN.cursor()
    if not isinstance(uidlist, list):
        raise ValueError('uidlist shold be list')
    int_uidlist = [str(uid) for uid in uidlist]
    q = 'select distinct item_id from userlist where user_id in (%s) and behavior_type=4' % ','.join(int_uidlist)
    cursor.execute(q)
    lines = cursor.fetchall()
    rec = [line[0] for line in lines]
    cursor.close()
    return rec

def get_buy_item_categories_of_mulitple_users_by_userid(uidlist):
    cursor = CONN.cursor()
    if not isinstance(uidlist, list):
        raise ValueError('uidlist shold be list')
    int_uidlist = [str(uid) for uid in uidlist]
    q = 'select distinct item_category from userlist where user_id in (%s) and behavior_type=4' % ','.join(int_uidlist)
    cursor.execute(q)
    lines = cursor.fetchall()
    rec = [line[0] for line in lines]
    cursor.close()
    return rec

def get_user_geo_by_uid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select distinct user_geohash from userlist where user_id=%s' % int_uid)
    line = cursor.fetchone()
    rec = {uid: str(line[0])}
    cursor.close()
    return rec

def get_buy_uid():
    cursor = CONN.cursor()
    cursor.execute('select distinct user_id from userlist where behavior_type=4')
    lines = cursor.fetchall()
    rec = [line[0] for line in lines]
    cursor.close()
    return rec

def get_user_buy_item_categories_by_userid(uid):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    cursor.execute('select distinct item_category from userlist where user_id=%s and behavior_type=4' % int_uid)
    lines = cursor.fetchall()
    rec = {uid: [str(line[0]) for line in lines]}
    cursor.close()
    return rec

def get_item_category_count_in_userlist():
    cursor = CONN.cursor()
    cursor.execute('select count(*) from userlist where behavior_type=4 group by item_category')
    lines = cursor.fetchall()
    rec = [str(line[0]) for line in lines]
    cursor.close()
    return rec

def get_all_user_selected():
    cursor = CONN.cursor()
    cursor.execute('select distinct user_id, count(*) from userlist group by user_id having count(*) >= 2 and behavior_type=4')
    lines = cursor.fetchall()
    rec = [line[0] for line in lines]
    cursor.close()
    return rec

def get_item_buy_times(tid):
    cursor = CONN.cursor()
    int_tid = tid
    if not isinstance(tid, int):
        int_tid = int(int_tid)
    cursor.execute('select count(*) from userlist group by item_id having behavior_type=4 and user_id=%s' % int_tid)
    lines = cursor.fetchall()
    rec = [int(line[0]) for line in lines]
    cursor.close()
    return rec