from recsys.algorithm.factorize import SVD
from util import userHandler
from recsys.datamodel.data import Data
import time

def preprocess(op_history_all_user):
    op_weight = [0, 0, 1, 1, 1]
    user_idx = {} # int, map from original id
    item_idx = {} # int, map from original id
    cat_idx = {}
    user_str = {} # str, original id of each mapped idx
    item_str = {} # str, original id of each mapped idx
    cat_str = {}
    user_op_item_cnt = {} # operation count [behavior=2,3,4] for each user on each item
    user_op_cat_cnt = {} # operation count [behavior=2,3,4] for each user on each cat
    item_op_users = {} # operation count [behavior=2,3,4] on each item by all user
    cat_op_users = {} # operation count [behavior=2,3,4] on each cat by all user
    user_op_cnt = {} # operation count [behavior=2,3,4] for each user
    cat_item_cnt = {}
    n_user = 1
    n_item = 1
    n_cat = 1

    for hi in op_history_all_user:
        # print hi
        # user info
        if hi[0] not in user_op_item_cnt:
            user_idx[hi[0]] = n_user
            user_str[n_user] = hi[0]
            n_user += 1
            user_op_cnt[hi[0]] = op_weight[hi[3]]
            user_op_item_cnt[hi[0]] = {}
            user_op_cat_cnt[hi[0]] = {}
        else:
            user_op_cnt[hi[0]] += op_weight[hi[3]]
        # item info
        if hi[1] not in item_op_users:
            item_idx[hi[1]] = n_item
            item_str[n_item] = hi[1]
            n_item += 1
            item_op_users[hi[1]] = op_weight[hi[3]]
        else:
            item_op_users[hi[1]] += op_weight[hi[3]]
        # category info
        if hi[2] not in cat_op_users:
            cat_idx[hi[2]] = n_cat
            cat_str[n_cat] = hi[2]
            n_cat += 1
            cat_op_users[hi[2]] = op_weight[hi[3]]
            cat_item_cnt[hi[2]] = {}
        else:
            cat_op_users[hi[2]] += op_weight[hi[3]]
        # user-item cnt
        if hi[1] not in user_op_item_cnt[hi[0]]:
            user_op_item_cnt[hi[0]][hi[1]] = op_weight[hi[3]]
        else:
            user_op_item_cnt[hi[0]][hi[1]] += op_weight[hi[3]]
        # cat-item cnt
        if hi[1] not in cat_item_cnt[hi[2]]:
            cat_item_cnt[hi[2]][hi[1]] = op_weight[hi[3]]
        else:
            cat_item_cnt[hi[2]][hi[1]] += op_weight[hi[3]]
        # user-cat cnt
        if hi[2] not in user_op_cat_cnt[hi[0]]:
            user_op_cat_cnt[hi[0]][hi[2]] = op_weight[hi[3]]
        else:
            user_op_cat_cnt[hi[0]][hi[2]] += op_weight[hi[3]]

    for ci in cat_item_cnt:
        cat_item_cnt[ci] = sorted(cat_item_cnt[ci].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)

    return user_idx, item_idx, cat_idx, user_str, item_str, cat_str, item_op_users, cat_op_users, user_op_cnt, user_op_item_cnt, user_op_cat_cnt, cat_item_cnt

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

def build_svd_user_cat_based(user_op_cat_cnt, cat_op_users, user_idx, cat_idx, min_nonzero):
    svd = SVD()
    data = Data()
    user_lst = []
    for ui in user_op_cat_cnt:
        if len(user_op_cat_cnt[ui]) < min_nonzero:
            continue
        for ci in user_op_cat_cnt[ui]:
            if cat_op_users[ci] < min_nonzero:
                continue
            if 1.0*user_op_cat_cnt[ui][ci] < 1:
                continue
            user_lst.append(ui)
            data.add_tuple(((1.0*user_op_cat_cnt[ui][ci]), user_idx[ui], cat_idx[ci]))
    user_lst = list(set(user_lst))
    print 'user =', len(user_lst)
    svd.set_data(data)
    return svd, user_lst

def build_svd_cat_based(user_op_cat_cnt, cat_op_users, user_idx, cat_idx, min_nonzero):
    svd = SVD()
    data = Data()
    cat_lst = []
    for ui in user_op_cat_cnt:
        if len(user_op_cat_cnt[ui]) < min_nonzero:
            continue
        for ci in user_op_cat_cnt[ui]:
            if cat_op_users[ci] < min_nonzero:
                continue
            if 1.0*user_op_cat_cnt[ui][ci] < 1:
                continue
            cat_lst.append(ci)
            data.add_tuple(((1.0*user_op_cat_cnt[ui][ci]), cat_idx[ci], user_idx[ui]))
    cat_lst = list(set(cat_lst))
    print 'cat =', len(cat_lst)
    svd.set_data(data)
    return svd, cat_lst

def svd_solver(svd, num_sigular):
    svd.compute(k=num_sigular,
                min_values=1, # remove lines full of zero
                pre_normalize=None,
                mean_center=False,
                post_normalize=True,
                savefile='svd_res')
    # print svd.get_matrix()
    return svd

def svd_user_similarity(svd, user_lst, user_idx, user_str, num_sim, sim_thr):
    sim_user = {}
    for ui in user_lst:
        sim_user[ui] = []
        tp_sim = svd.similar(int(user_idx[ui]), num_sim)
        for uj in tp_sim:
            if user_str[uj[0]] == ui:
                continue
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

def svd_user_cat_similarity(svd, user_lst, user_idx, user_str, num_sim, sim_thr):
    sim_user = {}
    for ui in user_lst:
        sim_user[ui] = []
        tp_sim = svd.similar(int(user_idx[ui]), num_sim)
        # print tp_sim
        for uj in tp_sim:
            if user_str[uj[0]] == ui:
                continue
            # print uj[1]
            if uj[1] > sim_thr:
                # print uj[1]
                sim_user[ui].append(user_str[uj[0]])
        # print sim_user[ui]
    return sim_user

def svd_cat_similarity(svd, cat_lst, cat_idx, cat_str, num_sim, sim_thr):
    sim_cat = {}
    for ti in cat_lst:
        sim_cat[ti] = []
        tp_sim = svd.similar(int(cat_idx[ti]), num_sim)
        for tj in tp_sim:
            # print tj[1]
            if tj[1] > sim_thr:
                sim_cat[ti].append(cat_str[tj[0]])
    return sim_cat

def recommendation_by_sim_user(recommendation_dict, user_buy_item, sim_user, user_op_item_cnt, user_op_cnt, op_ratio_thr):
    # print 'thr=', op_ratio_thr
    # for ui in sim_user:
    #     if ui not in recommendation_dict:
    #         recommendation_dict[ui] = []
    #     for uj in sim_user[ui]:
    #         for ti in user_op_item_cnt[uj]:
    #             # print user_op_item_cnt[uj][ti]
    #             # print user_op_cnt[uj]
    #             if 1.0*user_op_item_cnt[uj][ti]/(1.0*user_op_cnt[uj]) > op_ratio_thr:
    #                 # print 'here'
    #                 recommendation_dict[ui].append(ti)
    #         recommendation_dict[ui] = list(set(recommendation_dict[ui]))
    # return recommendation_dict
    for ui in sim_user:
        if ui not in recommendation_dict:
            recommendation_dict[ui] = []
        for uj in sim_user[ui]:
            if uj not in user_buy_item:
                continue
            for ti in user_buy_item[uj]:
                recommendation_dict[ui].append(ti)
            recommendation_dict[ui] = list(set(recommendation_dict[ui]))
        print recommendation_dict[ui]
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

def recommendation_by_sim_user_cat(recommendation_dict, user_buy_item, sim_user_cat, user_op_item_cnt, user_op_cnt, op_ratio_thr):
    # print 'thr=', op_ratio_thr
    for ui in sim_user_cat:
        if ui not in recommendation_dict:
            recommendation_dict[ui] = []
        for uj in sim_user_cat[ui]:
            if uj not in user_buy_item:
                continue
            for ti in user_buy_item[uj]:
                # print user_op_item_cnt[uj][ti]
                # print user_op_cnt[uj]
                # if 1.0*user_op_item_cnt[uj][ti]/(1.0*user_op_cnt[uj]) > op_ratio_thr:
                    # print 'here'
                recommendation_dict[ui].append(ti)
            recommendation_dict[ui] = list(set(recommendation_dict[ui]))
        print recommendation_dict[ui]
    return recommendation_dict

def recommendation_by_sim_cat(recommendation_dict, sim_cat, user_op_cat_cnt, user_buy_cat, cat_op_thr, cat_op_users, cat_item_cnt, min_cat_buy):
    for ui in user_buy_cat:
        if ui not in recommendation_dict:
            recommendation_dict[ui] = []
        for ci in user_buy_cat[ui]:
            if ci not in sim_cat:
                continue
            for cj in sim_cat[ci]:
                if cat_op_users[cj] > cat_op_thr:
                    for ti in cat_item_cnt[cj]:
                        if ti[1] < min_cat_buy:
                            break
                        recommendation_dict[ui].append(ti[0])
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

def recommendation(num_sigular, min_nonzero, num_sim_user, num_sim_item, num_sim_cat, sim_thr, min_user_op, op_ratio_thr, item_op_thr, cat_op_thr, min_cat_buy):
    t0=time.clock()

    op_history_all_user = userHandler.get_all_userid_and_itemid_and_behavior_type_no_distinct('traindataselect') #   traindataselecttotal
    # user_buy_item = userHandler.get_all_userid_and_itemid_distinct(4, 'trainbuydata') # databuytotal
    user_buy_cat = userHandler.get_all_userid_and_itemcat_distinct(4, 'trainbuydata')
    # item_cat = userHandler.get_all_itemid_and_itemcat('traindata')

    t1 = time.clock()
    print 'sql operation time:', t1 - t0

    recommendation_dict = {}

    user_idx, item_idx, cat_idx, user_str, item_str, cat_str, item_op_users, cat_op_users, user_op_cnt, user_op_item_cnt, user_op_cat_cnt, cat_item_cnt = preprocess(op_history_all_user)

    t2 = time.clock()
    print 'preprocess data time:', t2 - t1

    svd_user_based, user_lst = build_svd_user_based(user_op_item_cnt, item_op_users, user_idx, item_idx, min_nonzero)

    svd_user_based = svd_solver(svd_user_based, num_sigular)

    sim_user = svd_user_similarity(svd_user_based, user_lst, user_idx, user_str, num_sim_user, sim_thr)

    recommendation_dict = recommendation_by_sim_user(recommendation_dict, user_buy_item, sim_user, user_op_item_cnt, user_op_cnt, op_ratio_thr)
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
    print 'recommendation by self operation:', n_recomm_self_op - n_recomm_sim_item

    t5 = time.clock()
    print 'recommendation by self operation time:', t5 - t4

    svd_user_cat, user_lst = build_svd_user_cat_based(user_op_cat_cnt, cat_op_users, user_idx, cat_idx, min_nonzero)

    svd_user_cat = svd_solver(svd_user_cat, num_sigular)

    sim_user_cat = svd_user_cat_similarity(svd_user_cat, user_lst, user_idx, user_str, num_sim_user, sim_thr)

    recommendation_dict = recommendation_by_sim_user_cat(recommendation_dict, user_buy_item, sim_user_cat, user_op_item_cnt, user_op_cnt, op_ratio_thr)
    n_recomm_user_cat = 0
    for ui in recommendation_dict:
        n_recomm_user_cat += len(recommendation_dict[ui])
    print 'recommendation by user-cat similarity:', n_recomm_user_cat

    svd_cat_based, cat_lst = build_svd_cat_based(user_op_cat_cnt, cat_op_users, user_idx, cat_idx, min_nonzero)

    svd_cat_based = svd_solver(svd_cat_based, num_sigular)

    sim_cat = svd_cat_similarity(svd_cat_based, cat_lst, cat_idx, cat_str, num_sim_cat, sim_thr)

    recommendation_dict = recommendation_by_sim_cat(recommendation_dict, sim_cat, user_op_cat_cnt, user_buy_cat, cat_op_thr, cat_op_users, cat_item_cnt, min_cat_buy)
    n_recomm_sim_item = 0
    for ui in recommendation_dict:
        n_recomm_sim_item += len(recommendation_dict[ui])
    print 'recommendation by item similarity:', n_recomm_sim_item - n_recomm_sim_user

    return recommendation_dict

if __name__ == '__main__':
    print recommendation(100, 10, 10, 5, 5, 0.9, 0.1, 20)
