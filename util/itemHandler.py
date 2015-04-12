# -*- coding: utf-8 -*-
from util import dbHandler

USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']
#包括浏览、收藏、加购物车、购买，对应取值分别是1、2、3、4

def get_all_itemid():
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select distinct item_id from itemlist')
    lines = cursor.fetchall()
    rec = [str(line[0]) for line in lines]
    cursor.close()
    return rec

def get_all_item_category():
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select distinct item_category from itemlist')
    lines = cursor.fetchall()
    rec = [str(line[0]) for line in lines]
    cursor.close()
    return rec

def get_item_type_by_itemid(tid):
    cursor = dbHandler.CONN.cursor()
    int_tid = tid
    if not isinstance(tid, int):
        int_tid = int(int_tid)
    cursor.execute('select distinct item_category from itemlist where item_id=%s' % int_tid)
    line = cursor.fetchone()
    rec = {tid: str(line[0])}
    cursor.close()
    return rec

def get_item_by_item_type(item_type):
    cursor = dbHandler.CONN.cursor()
    if not isinstance(item_type, int):
        int_item_type = int(item_type)
    cursor.execute('select distinct item_id from itemlist where item_category=%s' % int_item_type)
    lines = cursor.fetchall()
    rec = {item_type: [str(line[0]) for line in lines]}
    cursor.close()
    return rec

def get_item_buytimes_buy_itemid(tid):
    cursor = dbHandler.CONN.cursor()
    if not isinstance(tid, int):
        int_tid = int(tid)
    q = 'select item_id, count(*) as item_buy_time from userlist '
    q += 'where userlist.behavior_type=4 '
    q += 'group by item_id '
    q += 'order by item_buy_time desc'
    cursor.execute(q)
    lines = cursor.fetchall()
    rec = {tid: [(str(line[0]), line[1]) for line in lines]}
    cursor.close()
    return rec[tid][:10]

def get_items_by_item_category(item_category):
    cursor = dbHandler.CONN.cursor()
    if not isinstance(item_category, basestring):
        item_category = int(item_category)
    cursor.execute('select distinct item_id from itemlist where item_category=%s' % item_category)
    lines = cursor.fetchall()
    rec = [str(line[0]) for line in lines]
    cursor.close()
    return rec
