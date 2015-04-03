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


    return usr_dict



# TODO:20150403
# 1.Separate raw data ordered by time (former 80% for training, later 20% for testing)
#     for training set, ouput as the original file
#     for testing set, only ouput the items whose corresponding 'behavior_type'==4, formation as: userid, item_id, .csv file too
#
# 2.Edit userHandle, output a dictionary usr_dict
# (key is userid, value is a list, each element in the list is a kind of data from original csv file,
# now I use the percentage of 'buy' operation of each user & total operation num of each user & count of operations on each item of each user)
# I'll finish feature_extraction before midnight today
#
# 3.sysEvaluation.py is used to test the system and output the final f-measure value
#
# 4.in itemHandler.py, output two dict, 'item_id'->'item_category', category change to 1~ncat, the dictionary named item_type_dict{} and 'item_category'->'item_id' named item_toid{}
#