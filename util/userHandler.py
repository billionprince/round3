import sqlite3
import settings
import os

DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']


def get_user_data_set_by_time(percent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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