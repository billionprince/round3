from util import timeHandler, dbHandler, fileHandler
import settings

TRAIN_DELETE_NOISY_DATA = 'traindata' #traindeletenoisydata  userlistwithoutnoisy
TRAIN_SCAN_TABLE = 'trainscandata'
TRAIN_CART_TABLE = 'traincartdata'
TRAIN_BUY_TABLE = 'trainbuydata'
USERLIST_WITHOUT_NOISY_TABLE_NAME = 'userlistwithoutnoisy'
USER_BEHAV_COUNT_TABLE_LAST_DAYS = 'user_behavior_cnt_last' # user_behavior_cnt_last_total
TRAIN_USER_BEHAV_CNT_TIME_TABLE = 'traincnttime' #'totalcnttime'
SELECTED_USER_BEHAV_CNT_TIME_TABLE = 'selectedusercnttime'
TARGET_USER_TABLE = 'target_user'
TEST_END_TIME = '2014-12-14 00'
TOTAL_END_TIME = '2014-12-15 23'

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


def user_beavior_based_recommendation(user_behav_cnt_time, user_behav_distri, user_buy_ratio, item_buy_ratio, user_behav_last_days, end_time, min_possi_ratio, min_buy_ratio):
    recommendation_dict = {}
    for ti in user_behav_last_days:
        recommendation_dict[ti[0]] = []
        if ti[0] not in user_behav_distri or ti[1] not in item_buy_ratio:
            continue
        if ti[2] == '4':
            pass
            # tp = [i for i in user_behav_cnt_time if ti[0]==i[0] and ti[1]==i[1]]
            # print 'tp=', tp
            # if tp:
            #     if (tp[0][4] and timeHandler.sub_days_of_two_time(tp[0][4], ti[5]) < 0) or (tp[0][2] and timeHandler.sub_days_of_two_time(tp[0][2], ti[5]) < 0):
            #         recommendation_dict[ti[0]].append(ti[1])
        else:
            days = timeHandler.sub_days_of_two_time(ti[5], end_time)
            user_interv_possibility = sum(user_behav_distri[ti[0]][0:days+1])
            if user_interv_possibility > min_possi_ratio and user_buy_ratio[ti[0]] > min_buy_ratio and item_buy_ratio[ti[1]] > 0:
                recommendation_dict[ti[0]].append(ti[1])
    # cnt = len(recommendation_dict)
    cnt = 0
    for ui in recommendation_dict:
        if recommendation_dict[ui]:
            recommendation_dict[ui] = list(set(recommendation_dict[ui]))
            cnt += len(recommendation_dict[ui])
    print 'num of recommendation:', cnt
    return recommendation_dict


def recommendation(max_day_interv, min_possi_ratio, min_buy_ratio, end_time, flush=False, isTest=True):
    init(flush, isTest, end_time)
    user_lst =dbHandler.read_table(TARGET_USER_TABLE)
    user_behav_cnt_time = dbHandler.read_table(SELECTED_USER_BEHAV_CNT_TIME_TABLE)
    user_behav_distri, user_buy_ratio, item_buy_ratio = user_buy_time_interval_distribution(user_behav_cnt_time, max_day_interv)

    user_behav_last_days = dbHandler.read_table(USER_BEHAV_COUNT_TABLE_LAST_DAYS)

    recommendation_dict = user_beavior_based_recommendation(user_behav_cnt_time, user_behav_distri, user_buy_ratio, item_buy_ratio, user_behav_last_days, end_time, min_possi_ratio, min_buy_ratio)
    return recommendation_dict

def init(flush=False, isTest=True, end_time=TEST_END_TIME):
    if not isTest: #prepare to submit
        flush = True
        TRAIN_DELETE_NOISY_DATA = 'userlistwithoutnoisy'
        end_time = TOTAL_END_TIME
    else:
        TRAIN_DELETE_NOISY_DATA = 'traindata'
    if flush:
        if dbHandler.table_exist(TARGET_USER_TABLE):
            dbHandler.delete_table(TARGET_USER_TABLE)
        if dbHandler.table_exist(USER_BEHAV_COUNT_TABLE_LAST_DAYS):
            dbHandler.delete_table(USER_BEHAV_COUNT_TABLE_LAST_DAYS)
        if dbHandler.table_exist(SELECTED_USER_BEHAV_CNT_TIME_TABLE):
            dbHandler.delete_table(SELECTED_USER_BEHAV_CNT_TIME_TABLE)
    if not dbHandler.table_exist(TARGET_USER_TABLE):
        cursor = dbHandler.CONN.cursor()
        print TRAIN_DELETE_NOISY_DATA
        q = 'select distinct user_id, count(*) from %s where behavior_type=4 group by user_id having count(*)>=3' % (TRAIN_DELETE_NOISY_DATA)
        cursor.execute(q)
        lines = cursor.fetchall()
        dbHandler.create_table(TARGET_USER_TABLE, ['user_id', 'num_buy'], lines, True)
        cursor.close()
    if not dbHandler.table_exist(SELECTED_USER_BEHAV_CNT_TIME_TABLE):
        cursor = dbHandler.CONN.cursor()
        q = 'select a.user_id, a.item_id, a.min_time, a.num_scan from '
        q += '(select user_id, item_id, min(time) as min_time, count(*) as num_scan from %s ' % TRAIN_DELETE_NOISY_DATA
        q += 'where behavior_type=1 group by user_id, item_id) a '
        q += 'join %s b on a.user_id=b.user_id' % TARGET_USER_TABLE
        cursor.execute(q)
        data = {(line[0], line[1]): [str(line[2]), line[3], 0, 0, 0, 0] for line in cursor.fetchall()}
        for line in cursor.fetchall():
            key = (line[0], line[1])
            if key not in data:
                data[key] = [0, 0, str(line[2]), line[3], 0, 0]
            else:
                data[key][2] = str(line[2])
                data[key][3] = line[3]
        q = 'select a.user_id, a.item_id, a.min_time, a.num_cart from '
        q += '(select user_id, item_id, min(time) as min_time, count(*) as num_cart from %s ' % TRAIN_DELETE_NOISY_DATA
        q += 'where behavior_type=3 group by user_id, item_id) a '
        q += 'join %s b on a.user_id=b.user_id' % TARGET_USER_TABLE
        cursor.execute(q)
        for line in cursor.fetchall():
            key = (line[0], line[1])
            if key not in data:
                data[key] = [0, 0, str(line[2]), line[3], 0, 0]
            else:
                data[key][2] = str(line[2])
                data[key][3] = line[3]
        q = 'select a.user_id, a.item_id, a.min_time, a.num_buy from '
        q += '(select user_id, item_id, min(time) as min_time, count(*) as num_buy from %s ' % TRAIN_DELETE_NOISY_DATA
        q += 'where behavior_type=4 group by user_id, item_id) a '
        q += 'join %s b on a.user_id=b.user_id' % TARGET_USER_TABLE
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
        dbHandler.create_table(SELECTED_USER_BEHAV_CNT_TIME_TABLE, title, lines, True)
        cursor.close()
    if not dbHandler.table_exist(USER_BEHAV_COUNT_TABLE_LAST_DAYS):
        cursor = dbHandler.CONN.cursor()
        q = 'select * from %s where time > "%s"' % (TRAIN_DELETE_NOISY_DATA, end_time)
        cursor.execute(q)
        lines = cursor.fetchall()
        dbHandler.create_table(USER_BEHAV_COUNT_TABLE_LAST_DAYS, USERLIST, lines, True)
        cursor.close()


if __name__ == '__main__':
# for running test, isTest set to True, for submit, isTest set to False, do not change others
    isTest = False
    flush = True
    end_time = TEST_END_TIME
    max_day_interv = 5
    min_possi_ratio = 0
    min_buy_ratio = 0

    recommendation_dict = recommendation(max_day_interv, min_possi_ratio, min_buy_ratio, end_time, flush, isTest)
    fileHandler.writeCsvFile(settings.OUTPUT_CSV, recommendation_dict, ['user_id', 'item_id'])
