from recsys.algorithm.factorize import SVD
from util import userHandler
from recsys.datamodel.data import Data


def svd_recommendation(num_sigular, min_nonzero, num_recomm, sim_thr):

    op_history_all_user = userHandler.get_all_userid_and_itemid_and_behavior_type_no_distinct('traindataselect')
    user_buy_item = userHandler.get_all_userid_and_itemid_distinct('trainbuydata') # list of item each user buy
    user_op_item_cnt = {} # operation count [behavior=2,3,4] for each user on each item
    item_op_users = {} # operation count [behavior=2,3,4] on each item by all user
    svd = SVD()
    data = Data()
    op_weight = [0, 0, 0.0001, 0.0001, 1000]
    user_idx = {} # int, map from original id
    item_idx = {} # int, map from original id
    user_str = {} # str, original id of each mapped idx
    item_str = {} # str, original id of each mapped idx
    n_user = 0
    n_item = 0

    for hi in op_history_all_user:
        if hi[0] not in user_op_item_cnt:
            user_idx[hi[0]] = n_user
            user_str[n_user] = hi[0]
            n_user += 1
            user_op_item_cnt[hi[0]] = {}
        if hi[1] not in item_op_users:
            item_idx[hi[1]] = n_item
            item_str[n_item] = hi[1]
            n_item += 1
            item_op_users[hi[1]] = 1
        else:
            item_op_users[hi[1]] += 1
        if hi[1] not in user_op_item_cnt[hi[0]]:
            user_op_item_cnt[hi[0]][hi[1]] = op_weight[hi[2]]
        else:
            user_op_item_cnt[hi[0]][hi[1]] += op_weight[hi[2]]

    item_lst = []
    user_lst = []
    for ui in user_op_item_cnt:
        if len(user_op_item_cnt[ui]) < min_nonzero:
            continue
        for ti in user_op_item_cnt[ui]:
            if item_op_users[ti] < min_nonzero:
                continue
            item_lst.append(ti)
            user_lst.append(ui)
            data.add_tuple((float(user_op_item_cnt[ui][ti]), user_idx[ui], item_idx[ti]))

    item_lst = list(set(item_lst))
    user_lst = list(set(user_lst))
    print 'num of selected item =', len(item_lst)
    print 'num of selected user =', len(user_lst)

    svd.set_data(data)

    svd.compute(k=num_sigular,
                min_values=1, # remove lines full of zero
                pre_normalize=None,
                mean_center=False,
                post_normalize=True,
                savefile='svd_res')

    recommendation_dict = {}

    for ui in user_lst:
        recommendation_dict[ui] = []
        tp_recomm_list = svd.similar(int(user_idx[ui]), num_recomm)
        for ti in tp_recomm_list:
            if ti[1] > sim_thr:
                recommendation_dict[ui].append(item_str[ti[0]])
                if item_str[ti[0]] in user_buy_item:
                    print 'here'
    return recommendation_dict

if __name__ == '__main__':
    print svd_recommendation(100, 10, 100, 0.7)

