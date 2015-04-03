from cluster import recommendation, DBSCAN
from util import userHandler, itemHandler
from evaluation import sysEvaluation

if __name__ == '__main__':
    try:
        user_dict = userHandler.build_user_feature_vector()
        user_classlabel, user_dict = DBSCAN.DBSCAN_user(user_dict)
        item_dict, item_type_dict, item_type_idx = itemHandler.item_input()
        recommendation_dict = recommendation.item_recommendation(user_classlabel, user_dict, user_mtx_id, item_type_dict, item_type_idx)
        F_measure = sysEvaluation.sysTest(recommendation_dict)
    except Exception as e:
        print e