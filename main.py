from cluster import recommendation, DBSCAN
from util import userHandler, itemHandler

if __name__ == '__main__':
    try:
        user_dict = userHandler.build_user_feature_vector()
        user_classlabel, user_dict = DBSCAN.DBSCAN_user(user_dict)
        item_dict, item_type_dict, item_type_idx = itemHandler.item_input()
        recommendation.item_recommendation(user_classlabel, user_dict, item_type_dict, item_type_idx)
    except Exception as e:
        print e