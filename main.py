from util import dbHandler, fileHandler
from cluster import SVD_based_recommendation
import settings

def calculate(data):
    gd_truth = dbHandler.read_table('testdata')
    num_recommend = sum([len(data[key]) for key in data])
    num_real_buy = len(gd_truth)
    user_set = set(map(int, data.keys()))
    hit_usr = len(set([line[0] for line in gd_truth]) & user_set)
    data_set = set((int(key), int(val)) for key in data for val in data[key])
    num_hit = len(set(gd_truth) & data_set)
    precision = float(num_hit) / num_recommend
    recall = float(num_hit) / num_real_buy
    F_measure = 2.0 * precision * recall / (precision + recall)

    print 'precision =', precision
    print 'recall=', recall
    print 'F_measure=', F_measure
    print 'total recommendation =',  num_recommend
    print 'hit_item =', num_hit
    print 'hit_user =', hit_usr
    print 'num of gdtruth =', num_real_buy

    return F_measure

if __name__ == '__main__':
    try:
        # user_dict = userHandler.build_user_feature_vector()
        # user_classlabel, user_dict = DBSCAN.DBSCAN_user(user_dict)
        # item_dict, item_type_dict, item_type_idx = itemHandler.item_input()
        # recommendation_dict = recommendation.item_recommendation(user_classlabel, user_dict, user_mtx_id, item_type_dict, item_type_idx)
        # recommendation_dict = recommendation.item_recommendation_single_user(num_recommend=1, min_buy_tiems=0)
        # recommendation_dict = graph_based_recommendation.recommendation(cat_sim_thr=0.0005, user_sim_thr=0.001, min_cat_sz=50, min_cat_thr=4, min_rec_per_cat=2)

        num_sigular = 100
        min_nonzero = 10
        num_sim_user = 0
        num_sim_item = 30
        sim_thr = 0.84
        min_user_op = 1
        op_ratio_thr = 0
        item_op_thr = 0
        # while num_sim_user < 40:
        #     print '(%d, %d, %d, %d, %.2f, %d, %.2f, %d)' % (num_sigular, min_nonzero, num_sim_user, num_sim_item, sim_thr, min_user_op, op_ratio_thr, item_op_thr)
        recommendation_dict = SVD_based_recommendation.recommendation(num_sigular, min_nonzero, num_sim_user, num_sim_item, sim_thr, min_user_op, op_ratio_thr, item_op_thr)
        # F_measure = calculate(recommendation_dict)
            # num_sim_user += 5
            # print '\n'
        fileHandler.writeCsvFile(settings.OUTPUT_CSV, recommendation_dict, ['user_id', 'item_id'])
    except Exception as e:
        print e