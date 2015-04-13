from util import dbHandler
from recsys.algorithm.factorize import SVD
from recsys.datamodel.data import Data


TRAIN_DELETE_NOISY_DATA = 'traindeletenoisydata'
TRAIN_SCAN_TABLE = 'trainscandata'
TRAIN_CART_TABLE = 'traincartdata'
TRAIN_BUY_TABLE = 'trainbuydata'
USERLIST_WITHOUT_NOISY_TABLE_NAME = 'userlistwithoutnoisy'
USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']

def preprocess(op_history_all_user):
    op_weight = [0, 0, 0, 0, 2]
    user_idx = {} # int, map from original id
    item_idx = {} # int, map from original id
    user_str = {} # str, original id of each mapped idx
    item_str = {} # str, original id of each mapped idx
    user_op_item_cnt = {} # operation count [behavior=2,3,4] for each user on each item
    user_op_cat_cnt = {} # operation count [behavior=2,3,4] for each user on each cat
    item_op_users = {} # operation count [behavior=2,3,4] on each item by all user
    user_op_cnt = {} # operation count [behavior=2,3,4] for each user
    n_user = 1
    n_item = 1

    for ui in op_history_all_user:
        if ui not in user_op_item_cnt:
            user_idx[ui] = n_user
            user_str[n_user] = ui
            n_user += 1
            user_op_cnt[ui] = 0
            user_op_item_cnt[ui] = {}
            user_op_cat_cnt[ui] = {}
        for i in op_history_all_user[ui]:
            ti = i[0]
            opi = i[1]
            user_op_cnt[ui] += op_weight[opi]
            if ti not in item_op_users:
                item_idx[ti] = n_item
                item_str[n_item] = ti
                n_item += 1
                item_op_users[ti] = 0
            item_op_users[ti] += op_weight[opi]
            if ti not in user_op_item_cnt[ui]:
                user_op_item_cnt[ui][ti] = op_weight[opi]
            else:
                user_op_item_cnt[ui][ti] += op_weight[opi]

    return user_idx, item_idx, user_str, item_str, item_op_users, user_op_cnt, user_op_item_cnt

def build_svd_item_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero):
    svd = SVD()
    data = Data()
    item_lst = []
    for ui in user_op_item_cnt:
        if len(user_op_item_cnt[ui]) < min_nonzero:
            continue
        for ti in user_op_item_cnt[ui]:
            if item_op_users[ti] < min_nonzero:
                continue
            if 1.0*user_op_item_cnt[ui][ti] < 1:
                continue
            item_lst.append(ti)
            data.add_tuple(((1.0*user_op_item_cnt[ui][ti]), item_idx[ti], user_idx[ui]))
    item_lst = list(set(item_lst))
    svd.set_data(data)
    return svd, item_lst

def svd_solver(svd, num_sigular):
    svd.compute(k=num_sigular,
                min_values=1, # remove lines full of zero
                pre_normalize=None,
                mean_center=False,
                post_normalize=True,
                savefile='svd_res')
    # print svd.get_matrix()
    return svd

def svd_based_classification(svd, item_lst, item_idx, item_str, sim_thr):
    sim_mtx = {}
    c_label = {}
    item_class = {}
    n_class = 0
    for ti in item_lst:
        sim_mtx[ti] = {}
        if ti not in c_label:
            c_label[ti] = n_class
            # print n_class
            n_class += 1
        tp_sim = svd.similar(int(item_idx[ti]), len(item_lst))
        for tj in tp_sim:
            if tj[1] > sim_thr:
                sim_mtx[ti][tj] = 0.0
                if item_str[tj[0]] not in c_label:
                    c_label[item_str[tj[0]]] = c_label[ti]
            else:
                sim_mtx[ti][tj] = 1e10
        if c_label[ti] not in item_class:
            item_class[c_label[ti]] = []
        item_class[c_label[ti]].append(ti)
    return sim_mtx, c_label, n_class, item_class

def recommendation(num_sigular, min_nonzero, sim_thr):

    # # === BEGIN Preprocess create table ===
    ## run script.py and get TRAIN_DELETE_NOISY_DATA and testdata
    ## if only want to calculate item similarity, only TRAIN_BUY_TABLE is needed, the other two table is built for recommendation
    # when testing use the sentence below:
    create_single_behavior_table(TRAIN_BUY_TABLE, TRAIN_DELETE_NOISY_DATA, 4)
    ## before submit, use the sentence below:
    # create_single_behavior_table(TRAIN_BUY_TABLE, USERLIST_WITHOUT_NOISY_TABLE_NAME, 4)
    # create_single_behavior_table(dbHandler.CONN, TRAIN_SCAN_TABLE, TRAIN_DELETE_NOISY_DATA, 1)
    # create_single_behavior_table(dbHandler.CONN, TRAIN_CART_TABLE, TRAIN_DELETE_NOISY_DATA, 3)
    # # === END Preprocess create table ===

    user_buy_his = get_all_userid_itemid_and_time_distinct(4, TRAIN_DELETE_NOISY_DATA)

    user_idx, item_idx, user_str, item_str, item_op_users, user_op_cnt, user_op_item_cnt = preprocess(user_buy_his)
    svd_item_based, item_lst = build_svd_item_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero)
    svd_item_based = svd_solver(svd_item_based, num_sigular)
    sim_mtx, c_label, n_class, item_class = svd_based_classification(svd_item_based, item_lst, item_idx, item_str, sim_thr)
    print c_label

    return c_label, item_lst, sim_mtx

def get_all_userid_itemid_and_time_distinct(btype, tableName='trainbuydata'):
    cursor = dbHandler.CONN.cursor()
    cursor.execute('select distinct user_id, item_id, behavior_type, time from %s where behavior_type=%s' % (tableName, btype))
    lines = cursor.fetchall()
    rec = {}
    for line in lines:
        if str(line[0]) not in rec:
            rec[str(line[0])] = []
        rec[str(line[0])].append([str(line[1]), int(line[2]), str(line[3])])
    return rec

def create_single_behavior_table(table_origin, table_new, btype):
    cursor = dbHandler.CONN.cursor()
    try:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % table_new)
        if cursor.fetchone():
            cursor.execute('drop table %s' % table_new)
        cursor.execute('create table %s as select * from %s where behavior_type=%s' % (table_new, table_origin, btype))
    except Exception as e:
        print e
        pass
    cursor.close()


if __name__ == '__main__':
    recommendation(100, 8, 0.05)

# INPUT parameters:
# num_sigular: num of sigular value in SVD, don't change
# min_nonzero: min num of nun-zero elements requied in a row or col in svd matrix, don't change
# sim_thr: when, similarity below this threshold, the similarity value will be set to INF
# OUTPUT parameters:
# clabel: a dict, key is item_id(str), value is the class_id the item belongs to
# item_lst: a list of item_id(str), the itemlst really used in svd, only these items are listed in c_label
# sim_mtx: a two level dict, similarity matrix of items, only item in item_lst will be in this matrix, key is item_id(str)
#          sim[itemid1][itemid2] = similarity_value