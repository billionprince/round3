import csv
from util import fileHandler
import settings
import feature_extraction

# def item_recommendation_DBSCAN(user_classlabel, user_dict, item_type_dict, item_type_idx):
#     csvfile = open('tianchi_mobile_recommend_train_user.csv')
#     #user_id item_id behavior_type user_geohash item_category time
#     csvfile.readline()
#
#     reader = csv.reader(csvfile)
#
#     class_num = len(user_classlabel)
#
#     userclass_item_cnt = [[0 for col in range(len(item_type_dict)+1)] for row in range(class_num)] # cnt of each category of item of each user class
#
#     for c in reader:
#         user_class = user_classlabel[user_dict[c[0]][4]]
#         if c[4] in item_type_dict and user_class != -1:
#             if c[2] == '4':
#                 userclass_item_cnt[user_class][item_type_dict[c[4]]] += 1
#
#
#     csvfile.close()

    
    # for i in range(class_num):
    #     final_itemlist = []
    #     for j in range(1, len(item_type_dict) + 1):
    #         final_itemlist.append((j, userclass_item_cnt[i][j]))
    #     final_itemlist.sort(key=lambda x:x[1], reverse=True)
    #     print final_itemlist
    #     for j in range(10): # for each user class, recommend 10 item categories
    #         print item_type_idx[final_itemlist[j][0]]

def item_recommendation_single_user(num_recommend, min_buy_tiems):

    user_dict, item_buy_dict = feature_extraction.build_user_feature_vector()

    recommendation_dict = {}

    for usr in user_dict:
        tp_recommend = []
        for item in user_dict[usr]:
            user_dict[usr][item][0] /= (1.0 * user_dict[usr][item][1])
        user_dict[usr] = sorted(user_dict[usr].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
        # print user_dict[usr]
        for i in range(len(user_dict[usr])):
            if user_dict[usr][i][1][1] > min_buy_tiems:
                if user_dict[usr][i][0] in item_buy_dict:
                    # print len(item_buy_dict[user_dict[usr][i][0]])
                    for j in range(len(item_buy_dict[user_dict[usr][i][0]])):
                        tp_recommend.append(item_buy_dict[user_dict[usr][i][0]][0][0])
        recommendation_dict[usr] = tp_recommend
        print recommendation_dict[usr]

    return recommendation_dict

if __name__ == '__main__':
    item_recommendation_single_user(num_recommend=1, min_buy_tiems=0)