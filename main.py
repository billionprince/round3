from cluster import recommendation
from util import userHandler, itemHandler
from evaluation import sysEvaluation
from cluster import recommendation

if __name__ == '__main__':
    try:
        # user_dict = userHandler.build_user_feature_vector()
        # user_classlabel, user_dict = DBSCAN.DBSCAN_user(user_dict)
        # item_dict, item_type_dict, item_type_idx = itemHandler.item_input()
        # recommendation_dict = recommendation.item_recommendation(user_classlabel, user_dict, user_mtx_id, item_type_dict, item_type_idx)
        recommendation_dict = recommendation.item_recommendation_single_user(num_recommend=1, min_buy_tiems=0)
        F_measure = sysEvaluation.sysTest(recommendation_dict)
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