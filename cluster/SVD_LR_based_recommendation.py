from util import dbHandler, userHandler
import itertools
from sklearn.linear_model import LogisticRegression

TESTDATA_TABLE_NO_NOISE = 'traindata'
USER_BEHAV_COUNT_TABLE = 'user_behavior_count'
USER_BEHAV_COUNT_TABLE_LAST_DAYS = 'user_behavior_count_last'
USER_BEHAV_LAST_DAYS_TABLE = 'user_behavior_last_days'
USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']

def get_LR_training_mtx(tableName):
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select * from %s' % tableName)
    lines = cursor.fetchall()
    user_behav_sample = {}
    user_behav_target = {}
    for line in lines:
        if line[0] not in user_behav_sample:
            user_behav_sample[line[0]] = []
            user_behav_target[line[0]] = []
        user_behav_sample[line[0]].append([float(line[2]), float(line[3])])
        user_behav_target[line[0]].append(float(line[4]))
    cursor.close()
    return user_behav_sample, user_behav_target

def recommendation():
    # # === BEGIN Preprocess create table ===
    # user_behavior_count(TESTDATA_TABLE_NO_NOISE, USER_BEHAV_COUNT_TABLE)
    # create_table_user_behavior_last_days(TESTDATA_TABLE_NO_NOISE, '2014-12-14 00')
    # user_behavior_count(USER_BEHAV_LAST_DAYS_TABLE, USER_BEHAV_COUNT_TABLE_LAST_DAYS)
    # # === END Preprocess create table ===

    user_behav_sample, user_behav_target = get_LR_training_mtx(USER_BEHAV_COUNT_TABLE)
    user_behav_last_days = get_userid_and_all_behavior_count(USER_BEHAV_COUNT_TABLE)

    recommendation_dict = {}
    for ui in user_behav_sample:
        if ui not in user_behav_last_days:
            continue
        recommendation_dict[ui] = []
        single_behav = 1 #no buy or all buy
        if len(list(set(user_behav_target[ui]))) == 2:
            single_behav = 0
            classifier = LogisticRegression()
            classifier.fit(user_behav_sample[ui], user_behav_target[ui])
        for ti in user_behav_last_days[ui]:
            if ti[2] != 0:
                continue
            if single_behav == 1:
                if user_behav_target[ui][0] == 1:
                    recommendation_dict[ui].append(ti[0])
            elif classifier.predict([ti[1], ti[2]]) == 1:
                recommendation_dict[ui].append(ti[0])
        print recommendation_dict[ui]

    return recommendation_dict

def user_behavior_count(tableName_input, tableName_output):
    cursor = dbHandler.CONN.cursor()
    q = 'select user_id, item_id, count(*) as num_scan from %s ' % tableName_input
    q += 'where behavior_type=1 group by user_id, item_id'
    cursor.execute(q)
    data = {(line[0], line[1]): [line[2], 0, 0] for line in cursor.fetchall()}
    q = 'select user_id, item_id, count(*) as num_cart from %s ' % tableName_input
    q += 'where behavior_type=3 group by user_id, item_id'
    cursor.execute(q)
    for line in cursor.fetchall():
        key = (line[0], line[1])
        if key not in data:
            data[key] = [0, line[2], 0]
        else:
            data[key][1] = line[2]
    q = 'select user_id, item_id, count(*) as num_buy from %s ' % tableName_input
    q += 'where behavior_type=4 group by user_id, item_id'
    cursor.execute(q)
    for line in cursor.fetchall():
        key = (line[0], line[1])
        if key not in data:
            data[key] = [0, 0, line[2]]
        else:
            data[key][2] = line[2]
    title = ['user_id', 'item_id', 'num_scan', 'num_cart', 'num_buy']
    lines = [list(k) + v for k, v in data.iteritems()]
    dbHandler.create_table(tableName_output, title, lines, True)
    cursor.close()

def create_table_user_behavior_last_days(tableName, time):
    cursor = dbHandler.CONN.cursor()
    q = 'select * from %s where time > "%s"' % (tableName, time)
    cursor.execute(q)
    lines = cursor.fetchall()
    dbHandler.create_table(USER_BEHAV_LAST_DAYS_TABLE, USERLIST, lines, True)
    cursor.close()

def get_columns(tableName='traindata'):
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select * from %s' % (tableName))
    lines = cursor.fetchall()
    rec = [line[0] for line in lines]
    cursor.close()
    return rec

def get_all_userid_itemid_behavior_count(tableName='user_behavior_count'):
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select user_id, item_id, num_scan, num_cart, num_buy from %s' % (tableName))
    lines = cursor.fetchall()
    rec = {}
    for line in lines:
        if str(line[0]) not in rec:
            rec[str(line[0])] = []
        rec[str(line[0])].append([str(line[1]), int(line[2]), int(line[3]), int(line[4])])
    return rec

def get_userid_and_all_behavior_count(tableName='trainbuydata'):
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select user_id, item_id, num_scan, num_cart, num_buy from %s' % (tableName))
    lines = cursor.fetchall()
    rec = {}
    for line in lines:
        if str(line[0]) not in rec:
            rec[str(line[0])] = []
        rec[str(line[0])].append([str(line[1]), int(line[2]), int(line[3]), int(line[4])])
    return rec

if __name__ == '__main__':
    recommendation()


