from recsys.algorithm.factorize import SVD
from util import userHandler
from recsys.datamodel.data import Data
import time

def preprocess(op_history_all_user):
    op_weight = [0, 0, 0, 0, 2]
    user_idx = {} # int, map from original id
    item_idx = {} # int, map from original id
    user_str = {} # str, original id of each mapped idx
    item_str = {} # str, original id of each mapped idx
    user_op_item_cnt = {} # operation count [behavior=2,3,4] for each user on each item
    item_op_users = {} # operation count [behavior=2,3,4] on each item by all user
    user_op_cnt = {} # operation count [behavior=2,3,4] for each user
    n_user = 1
    n_item = 1

    for hi in op_history_all_user:
        if hi[0] not in user_op_item_cnt:
            user_idx[hi[0]] = n_user
            user_str[n_user] = hi[0]
            n_user += 1
            user_op_cnt[hi[0]] = op_weight[hi[2]]
            user_op_item_cnt[hi[0]] = {}
        else:
            user_op_cnt[hi[0]] += op_weight[hi[2]]
        if hi[1] not in item_op_users:
            item_idx[hi[1]] = n_item
            item_str[n_item] = hi[1]
            n_item += 1
            item_op_users[hi[1]] = op_weight[hi[2]]
        else:
            item_op_users[hi[1]] += op_weight[hi[2]]
        if hi[1] not in user_op_item_cnt[hi[0]]:
            user_op_item_cnt[hi[0]][hi[1]] = op_weight[hi[2]]
        else:
            user_op_item_cnt[hi[0]][hi[1]] += op_weight[hi[2]]

    return user_idx, item_idx, user_str, item_str, item_op_users, user_op_cnt, user_op_item_cnt

def build_svd_user_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero):
    svd = SVD()
    data = Data()
    user_lst = []
    for ui in user_op_item_cnt:
        if len(user_op_item_cnt[ui]) < min_nonzero:
            continue
        for ti in user_op_item_cnt[ui]:
            if item_op_users[ti] < min_nonzero:
                continue
            if 1.0*user_op_item_cnt[ui][ti] < 1:
                continue
            user_lst.append(ui)
            data.add_tuple(((1.0*user_op_item_cnt[ui][ti]), user_idx[ui], item_idx[ti]))
    user_lst = list(set(user_lst))
    svd.set_data(data)
    print 'user =', len(user_lst)
    return svd, user_lst

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
    print 'item =', len(item_lst)
    svd.set_data(data)
    return svd, item_lst

def svd_solver(svd, num_sigular):
    svd.compute(k=num_sigular,
                min_values=1, # remove lines full of zero
                pre_normalize=None,
                mean_center=False,
                post_normalize=True,
                savefile='svd_res')
    return svd

def svd_user_similarity(svd, user_lst, user_idx, user_str, num_sim, sim_thr):
    sim_user = {}
    for ui in user_lst:
        sim_user[ui] = []
        tp_sim = svd.similar(int(user_idx[ui]), num_sim)
        for uj in tp_sim:
            if uj[1] > sim_thr:
                # print uj[1]
                sim_user[ui].append(user_str[uj[0]])
    return sim_user

def svd_item_similarity(svd, item_lst, item_idx, item_str, num_sim, sim_thr):
    sim_item = {}
    for ti in item_lst:
        sim_item[ti] = []
        tp_sim = svd.similar(int(item_idx[ti]), num_sim)
        for tj in tp_sim:
            # print tj[1]
            if tj[1] > sim_thr:
                sim_item[ti].append(item_str[tj[0]])
    return sim_item

def recommendation_by_sim_user(recommendation_dict, sim_user, user_op_item_cnt, user_op_cnt, op_ratio_thr):
    for ui in sim_user:
        if ui not in recommendation_dict:
            recommendation_dict[ui] = []
        for uj in sim_user[ui]:
            for ti in user_op_item_cnt[uj]:
                if 1.0*user_op_item_cnt[uj][ti]/(1.0*user_op_cnt[uj]) > op_ratio_thr:
                    recommendation_dict[ui].append(ti)
            recommendation_dict[ui] = list(set(recommendation_dict[ui]))
    return recommendation_dict

def recommendation_by_sim_item(recommendation_dict, sim_item, user_op_item_cnt, item_op_users, user_buy_item, item_op_thr):
    for ui in user_buy_item:
        if ui not in recommendation_dict:
            recommendation_dict[ui] = []
        for ti in user_buy_item[ui]:
            if ti not in sim_item:
                continue
            for tj in sim_item[ti]:
                if item_op_users[tj] > item_op_thr:
                    recommendation_dict[ui].append(ti)
            recommendation_dict[ui] = list(set(recommendation_dict[ui]))
    return recommendation_dict

def recommendation_by_self_op_history(recommendation_dict, user_buy_item, user_op_item_cnt, user_op_cnt, min_user_op, op_ratio_thr):
    for ui in user_buy_item:
        if user_op_cnt[ui] < min_user_op:
            continue
        if ui not in recommendation_dict:
            recommendation_dict[ui] = []
        for ti in user_buy_item[ui]:
            if 1.0*user_op_item_cnt[ui][ti]/(1.0*user_op_cnt[ui]) > op_ratio_thr:
                recommendation_dict[ui].append(ti)
        recommendation_dict[ui] = list(set(recommendation_dict[ui]))
    return recommendation_dict

def recommendation(num_sigular, min_nonzero, num_sim_user, num_sim_item, sim_thr, op_ratio_thr, item_op_thr, min_user_op):
    t0=time.clock()

    op_history_all_user = userHandler.get_all_userid_and_itemid_and_behavior_type_no_distinct('traindataselecttotal') #  traindataselect
    user_buy_item = userHandler.get_all_userid_and_itemid_distinct(4, 'databuytotal') #  trainbuydata
    cnt = 0
    for ui in user_buy_item:
        cnt += len(user_buy_item[ui])
    print 'cnt=', cnt
    t1 = time.clock()
    print 'sql operation time:', t1 - t0

    recommendation_dict = {}

    user_idx, item_idx, user_str, item_str, item_op_users, user_op_cnt, user_op_item_cnt = preprocess(op_history_all_user)

    t2 = time.clock()
    print 'preprocess data time:', t2 - t1

    svd_user_based, user_lst = build_svd_user_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero)

    svd_user_based = svd_solver(svd_user_based, num_sigular)

    sim_user = svd_user_similarity(svd_user_based, user_lst, user_idx, user_str, num_sim_user, sim_thr)

    recommendation_dict = recommendation_by_sim_user(recommendation_dict, sim_user, user_op_item_cnt, user_op_cnt, op_ratio_thr)
    n_recomm_sim_user = 0
    for ui in recommendation_dict:
        n_recomm_sim_user += len(recommendation_dict[ui])
    print 'recommendation by user similarity:', n_recomm_sim_user

    t3 = time.clock()
    print 'recommendation by user similarity time:', t3 - t2

    svd_item_based, item_lst = build_svd_item_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero)

    svd_item_based = svd_solver(svd_item_based, num_sigular)

    sim_item = svd_item_similarity(svd_item_based, item_lst, item_idx, item_str, num_sim_item, sim_thr)

    recommendation_dict = recommendation_by_sim_item(recommendation_dict, sim_item, user_op_item_cnt, item_op_users, user_buy_item, item_op_thr)
    n_recomm_sim_item = 0
    for ui in recommendation_dict:
        n_recomm_sim_item += len(recommendation_dict[ui])
    print 'recommendation by item similarity:', n_recomm_sim_item - n_recomm_sim_user

    t4 = time.clock()
    print 'recommendation by item similarity time:', t4 - t3

    recommendation_dict = recommendation_by_self_op_history(recommendation_dict, user_buy_item, user_op_item_cnt, user_op_cnt, min_user_op, op_ratio_thr)
    n_recomm_self_op = 0
    for ui in recommendation_dict:
        n_recomm_self_op += len(recommendation_dict[ui])
    print 'recommendation by self operation:', n_recomm_self_op# - n_recomm_sim_item

    t5 = time.clock()
    print 'recommendation by self operation time:', t5 - t4

    return recommendation_dict

if __name__ == '__main__':
    print recommendation(100, 10, 10, 5, 5, 0.9, 0.1, 20)
