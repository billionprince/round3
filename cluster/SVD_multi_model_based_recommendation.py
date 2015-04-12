import sqlite3
from util import userHandler, timeHandler
import os
import settings
from recsys.algorithm.factorize import SVD
from recsys.datamodel.data import Data

DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
CONN = sqlite3.connect(DB_PATH)
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
    print n_class
    return sim_mtx, c_label, n_class, item_class

def item_class_analysis(item_op_users, c_label, n_class, item_class, item_lst):
    class_buy_cnt = {}
    for ti in item_lst:
        if c_label[ti] not in class_buy_cnt:
            class_buy_cnt[c_label[ti]] = []
        class_buy_cnt[c_label[ti]].append((ti, item_op_users[ti]))
    for ci in range(n_class):
        class_buy_cnt[ci] = sorted(class_buy_cnt[ci], lambda x, y: cmp(x[1], y[1]), reverse = True)
    return class_buy_cnt


def op_history_based_recommendation(recommendation_dict, class_buy_cnt, user_buy_his, user_scan_his, user_cart_his, trans_ratio, day_thr):

    user_id = userHandler.get_all_uid('traindata')
    user_p14 = {}
    user_p34 = {}

    for ui in user_id:
        cnt_buy, cnt_cart, cnt_scan, user_p14[ui], user_p34[ui] = 0, 0, 0, 0, 0
        if ui in user_buy_his:
            cnt_buy = len(user_buy_his[ui])
        if ui in user_scan_his:
            cnt_scan = len(user_scan_his[ui])
        if ui in user_cart_his:
            cnt_cart = len(user_cart_his[ui])
        if cnt_scan > 0:
            user_p14[ui] = 1.0*cnt_buy/cnt_scan
        if cnt_cart > 0:
            user_p34[ui] = 1.0*cnt_buy/cnt_cart
        recommendation_dict[ui] = []
        if user_p14[ui] > trans_ratio:
            for ti in user_scan_his[ui]:
                if timeHandler.sub_days_of_two_time(ti[2], '2014-12-16 00') < day_thr:
                    if ti not in user_buy_his[ui]:
                        recommendation_dict[ui].append(ti[0])
                    else:
                        recommendation_dict[ui].append(class_buy_cnt[ti[0]][0][0])
        if user_p34[ui] > trans_ratio:
            for ti in user_cart_his[ui]:
                if timeHandler.sub_days_of_two_time(ti[2], '2014-12-16 00') < day_thr:
                    if ti not in user_buy_his[ui]:
                        recommendation_dict[ui].append(ti[0])
                    else:
                        recommendation_dict[ui].append(class_buy_cnt[ti[0]][0][0])
        recommendation_dict[ui] = list(set(recommendation_dict[ui]))
        if len(recommendation_dict[ui]) == 0:
            recommendation_dict.pop(ui)
    return recommendation_dict

def recommendation(num_sigular, min_nonzero, sim_thr, trans_ratio, day_thr):
    user_buy_his = userHandler.get_all_userid_itemid_and_time_distinct(4, 'trainbuydata')

    user_scan_his = userHandler.get_all_userid_itemid_and_time_distinct(1, 'trainscandata')

    user_cart_his = userHandler.get_all_userid_itemid_and_time_distinct(3, 'traincartdata')

    # t1 = time.clock()
    # print 'sql operation time:', t1 - t0

    recommendation_dict = {}

    user_idx, item_idx, user_str, item_str, item_op_users, user_op_cnt, user_op_item_cnt = preprocess(user_buy_his)
    svd_item_based, item_lst = build_svd_item_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero)

    svd_item_based = svd_solver(svd_item_based, num_sigular)

    sim_mtx, c_label, n_class, item_class = svd_based_classification(svd_item_based, item_lst, item_idx, item_str, sim_thr)

    class_buy_cnt = item_class_analysis(item_op_users, c_label, n_class, item_class, item_lst)

    recommendation_dict = op_history_based_recommendation(recommendation_dict, class_buy_cnt, user_buy_his, user_scan_his, user_cart_his, trans_ratio, day_thr)

    return recommendation_dict


if __name__ == '__main__':
    recommendation(100, 8, 0.1, 0.5, 3)