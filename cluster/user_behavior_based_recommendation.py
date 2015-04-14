from util import timeHandler, dbHandler


TRAIN_DELETE_NOISY_DATA = 'userlistwithoutnoisy' #traindeletenoisydata traindata
TRAIN_SCAN_TABLE = 'trainscandata'
TRAIN_CART_TABLE = 'traincartdata'
TRAIN_BUY_TABLE = 'trainbuydata'
USERLIST_WITHOUT_NOISY_TABLE_NAME = 'userlistwithoutnoisy'
USER_BEHAV_COUNT_TABLE_LAST_DAYS = 'user_behavior_cnt_last_total' #user_behavior_cnt_last
TRAIN_USER_BEHAV_CNT_TIME_TABLE = 'totalcnttime' #traincnttime

USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']


def user_buy_time_interval_distribution(user_behav_cnt_time, max_day_interv):
    user_op_time_interv, item_op_time_interv, item_buy_ratio, user_buy_ratio, user_behav_distri = {}, {}, {}, {}, {}
    for ui in user_behav_cnt_time:
        if ui[0] not in user_op_time_interv:
            user_op_time_interv[ui[0]] = []
        if ui[1] not in item_op_time_interv:
            item_op_time_interv[ui[1]] = []
        if int(ui[7]):
            if int(ui[3]):
                tp_interval = timeHandler.sub_days_of_two_time(ui[2], ui[6])
                if tp_interval > 0:
                    user_op_time_interv[ui[0]].append(tp_interval)
                    item_op_time_interv[ui[1]].append(tp_interval)
            if int(ui[5]):
                tp_interval = timeHandler.sub_days_of_two_time(ui[4], ui[6])
                if tp_interval > 0:
                    user_op_time_interv[ui[0]].append(tp_interval)
                    item_op_time_interv[ui[1]].append(tp_interval)
        else:
            user_op_time_interv[ui[0]].append(-1)
            item_op_time_interv[ui[1]].append(-1)
    for ui in user_op_time_interv:
        tp_sum = len([di for di in user_op_time_interv[ui] if di >= 0])
        if tp_sum == 0:
            continue
        user_behav_distri[ui] = [float(user_op_time_interv[ui].count(di))/float(tp_sum) for di in range(0, max_day_interv)]
        user_buy_ratio[ui] = float(len([i for i in user_op_time_interv[ui] if i >= 0]))/float(len(user_op_time_interv[ui]))
    for ti in item_op_time_interv:
        if len(item_op_time_interv[ti]) > 0:
            item_buy_ratio[ti] = float(len([i for i in item_op_time_interv[ti] if i >= 0]))/float(len(item_op_time_interv[ti]))
    return user_behav_distri, user_buy_ratio, item_buy_ratio


def user_beavior_based_recommendation(user_behav_distri, user_buy_ratio, item_buy_ratio, user_behav_last_days, min_possi_ratio, min_buy_ratio):
    recommendation_dict = {}
    for ti in user_behav_last_days:
        if ti[0] not in user_behav_distri or ti[2] == '4':
            continue
        recommendation_dict[ti[0]] = []
        days = timeHandler.sub_days_of_two_time(ti[5], '2014-12-16 23')
        user_interv_possibility = sum(user_behav_distri[ti[0]][0:days+1])
        if user_interv_possibility > min_possi_ratio and user_buy_ratio[ti[0]]> min_buy_ratio and item_buy_ratio[ti[1]] > min_buy_ratio:
            recommendation_dict[ti[0]].append(ti[1])
    cnt = 0
    for ui in recommendation_dict:
        if recommendation_dict[ui]:
            recommendation_dict[ui] = list(set(recommendation_dict[ui]))
            cnt += len(recommendation_dict[ui])
    print cnt
    return recommendation_dict


def recommendation(max_day_interv, min_possi_ratio, min_buy_ratio):

    user_behav_cnt_time = dbHandler.read_table(TRAIN_USER_BEHAV_CNT_TIME_TABLE)

    user_behav_distri, user_buy_ratio, item_buy_ratio = user_buy_time_interval_distribution(user_behav_cnt_time, max_day_interv)
    print 'end1'
    user_behav_last_days = dbHandler.read_table(USER_BEHAV_COUNT_TABLE_LAST_DAYS)
    print 'end2'
    recommendation_dict = user_beavior_based_recommendation(user_behav_distri, user_buy_ratio, item_buy_ratio, user_behav_last_days, min_possi_ratio, min_buy_ratio)
    print 'end3'
    return recommendation_dict


def create_table_user_behavior_last_days(tableName_input, tableName_output, time):
    cursor = dbHandler.CONN.cursor()
    q = 'select * from %s where time > "%s"' % (tableName_input, time)
    cursor.execute(q)
    lines = cursor.fetchall()
    dbHandler.create_table(tableName_output, USERLIST, lines, True)
    cursor.close()


def user_behavior_count_and_time_distinct(tableName_input, tableName_output):
    cursor = dbHandler.CONN.cursor()
    q = 'select user_id, item_id, min(time), count(*) as num_scan from %s ' % tableName_input
    q += 'where behavior_type=1 group by user_id, item_id'
    cursor.execute(q)
    data = {(line[0], line[1]): [str(line[2]), line[3], 0, 0, 0, 0] for line in cursor.fetchall()}
    q = 'select user_id, item_id, min(time), count(*) as num_cart from %s ' % tableName_input
    q += 'where behavior_type=3 group by user_id, item_id'
    cursor.execute(q)
    for line in cursor.fetchall():
        key = (line[0], line[1])
        if key not in data:
            data[key] = [0, 0, str(line[2]), line[3], 0, 0]
        else:
            data[key][2] = str(line[2])
            data[key][3] = line[3]
    q = 'select user_id, item_id, min(time), count(*) as num_buy from %s ' % tableName_input
    q += 'where behavior_type=4 group by user_id, item_id'
    cursor.execute(q)
    for line in cursor.fetchall():
        key = (line[0], line[1])
        if key not in data:
            data[key] = [0, 0, 0, 0, str(line[2]), line[3]]
        else:
            data[key][4] = str(line[2])
            data[key][5] = line[3]
    title = ['user_id', 'item_id', 'initial_scan_time', 'num_scan', 'initial_cart_time', 'num_cart', 'initial_buy_time', 'num_buy']
    lines = [list(k) + v for k, v in data.iteritems()]
    dbHandler.create_table(tableName_output, title, lines, True)
    dbHandler.CONN.commit()
    # cursor.close()

 # BEGIN Preprocess --- create table
    # user_behavior_count_and_time_distinct(TRAIN_DELETE_NOISY_DATA, TRAIN_USER_BEHAV_CNT_TIME_TABLE)
    # create_table_user_behavior_last_days(TRAIN_DELETE_NOISY_DATA, USER_BEHAV_COUNT_TABLE_LAST_DAYS, '2014-12-14 00')
    # END Preprocess --- create table

def init(tableName_input, tableName_output, flush=False):
    if flush:
        if dbHandler.table_exist(TRAIN_USER_BEHAV_CNT_TIME_TABLE):
            dbHandler.delete_table(TRAIN_USER_BEHAV_CNT_TIME_TABLE)
        if dbHandler.table_exist(USER_BEHAV_COUNT_TABLE_LAST_DAYS):
            dbHandler.delete_table(USER_BEHAV_COUNT_TABLE_LAST_DAYS)
    if not dbHandler.table_exist(TRAIN_USER_BEHAV_CNT_TIME_TABLE):
        cursor = dbHandler.CONN.cursor()
        q = 'select user_id, item_id, min(time), count(*) as num_scan from %s ' % tableName_input
        q += 'where behavior_type=1 group by user_id, item_id'
        cursor.execute(q)
        data = {(line[0], line[1]): [str(line[2]), line[3], 0, 0, 0, 0] for line in cursor.fetchall()}
        q = 'select user_id, item_id, min(time), count(*) as num_cart from %s ' % tableName_input
        q += 'where behavior_type=3 group by user_id, item_id'
        cursor.execute(q)
        for line in cursor.fetchall():
            key = (line[0], line[1])
            if key not in data:
                data[key] = [0, 0, str(line[2]), line[3], 0, 0]
            else:
                data[key][2] = str(line[2])
                data[key][3] = line[3]
        q = 'select user_id, item_id, min(time), count(*) as num_buy from %s ' % tableName_input
        q += 'where behavior_type=4 group by user_id, item_id'
        cursor.execute(q)
        for line in cursor.fetchall():
            key = (line[0], line[1])
            if key not in data:
                data[key] = [0, 0, 0, 0, str(line[2]), line[3]]
            else:
                data[key][4] = str(line[2])
                data[key][5] = line[3]
        title = ['user_id', 'item_id', 'initial_scan_time', 'num_scan', 'initial_cart_time', 'num_cart', 'initial_buy_time', 'num_buy']
        lines = [list(k) + v for k, v in data.iteritems()]
        dbHandler.create_table(tableName_output, title, lines, True)
        dbHandler.CONN.commit()
    if not dbHandler.table_exist(USER_BEHAV_COUNT_TABLE_LAST_DAYS):
        cursor = dbHandler.CONN.cursor()
        q = 'select * from %s where time > "%s"' % (tableName_input, time)
        cursor.execute(q)
        lines = cursor.fetchall()
        dbHandler.create_table(tableName_output, USERLIST, lines, True)
        cursor.close()


if __name__ == '__main__':
    recommendation(6, 0.5, 0.3)