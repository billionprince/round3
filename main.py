from util import userHandler, itemHandler, fileHandler
from evaluation import sysEvaluation
from cluster import SVD_based_recommendation
import settings

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
        # F_measure = sysEvaluation.sysTest(recommendation_dict)
            # num_sim_user += 5
            # print '\n'
        fileHandler.writeCsvFile(settings.OUTPUT_CSV, recommendation_dict, ['user_id', 'item_id'])
    except Exception as e:
        print e


# TODO:20150404
# 1. In function fileHandler.readFile, '\r' is not stripped, problems will occur when I call it
# 2. Finish separating the whole data set, (fixed, 80%, 20%) according to what I said yesterday
# 3. I think the function fileHandler.readFile is convenient now,
#    can I keep using it before determining which better ML model to use?
# 4. In this version, recommendation.item_recommendation_single_user can give the final recommendation
#    using a very naive strategy, only to get a initial result. The data is more sparser than I imagine,
#    such as, I read 10w lines of user file, each item category only contains one item, etc.
#    I'll keep on finding more algorithms in ML.
#    Now, sysTest can output Precision, Recall and F_measure, maybe we can test it today if you are free.
# Any problem, please contact me, thx for the help :)