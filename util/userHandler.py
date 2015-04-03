from util import fileHandler
import settings

def build_user_feature_vector():
    lines = fileHandler.readFile(settings.USER_FILE, 1200000) # 12312542

    usr_dict = {}
    # user_item_cat_dict = {} # items have been bought by user
    user_item_buy_dict = {}
    # nitem = 0

    for line in lines:
        username = line['user_id']
        if username not in usr_dict:
            usr_dict[username] = [0., 0., 0., 0.] # percentage of buy, total op, recommend 1, recommend2
            user_item_buy_dict[username] = {}
        itemcat = line['item_category']
        # if itemcat not in user_item_cat_dict:
        #     user_item_cat_dict[itemcat] = nitem
        #     nitem += 1
        # usr_dict[username][int(line['behavior_type'])-1] += 1
        if int(line['behavior_type']) == 4:
            usr_dict[username][0] += 1
            # print user_item_buy_dict[username]
        if itemcat not in user_item_buy_dict[username]:
            user_item_buy_dict[username][itemcat] = 1
        else:
            user_item_buy_dict[username][itemcat] += 1
        usr_dict[username][1] += 1

    # print user_item_buy_dict
    # imax = 0
    # print usr_dict


    for usr in usr_dict:
        user_item_buy_dict[usr] = sorted(user_item_buy_dict[usr].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
        if len(user_item_buy_dict[usr]) > 2:
            usr_dict[usr][2] = user_item_buy_dict[usr][0][0]
            usr_dict[usr][3] = user_item_buy_dict[usr][1][0]
            # print usr_dict[usr]
        # print user_item_buy_dict[usr]
        # imax = max(imax, usr_dict[usr][1])
        if usr_dict[usr][1] > 0:
            usr_dict[usr][0] /= usr_dict[usr][1]



        # tot = sum(usr_dict[usr][:3])
        # usr_dict[usr] = [val/tot for val in usr_dict[usr]]
    return usr_dict