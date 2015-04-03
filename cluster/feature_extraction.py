from util import userHandler, itemHandler, fileHandler
import settings

def build_user_feature_vector():
    # for usr in user_dict:
    #     user_item_buy_dict[usr] = sorted(user_item_buy_dict[usr].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
    #     if len(user_item_buy_dict[usr]) > 2:
    #         user_dict[usr][2] = user_item_buy_dict[usr][0][0]
    #         user_dict[usr][3] = user_item_buy_dict[usr][1][0]
    #         # print usr_dict[usr]
    #     # print user_item_buy_dict[usr]
    #     # imax = max(imax, usr_dict[usr][1])
    #     if user_dict[usr][1] > 0:
    #         user_dict[usr][0] /= user_dict[usr][1]


    # lines = fileHandler.readFile(settings.ITEM_FILE, 100000)
    #
    # item_dict = {}
    #
    # for line in lines:
    #     print line
    #     break
    #     if line['item_category'] not in item_dict:
    #         item_dict[line['item_category']] = {}
    #     if line['item_id'] not in item_dict[line['item_category']]:
    #         item_dict[line['item_category']][line['item_id']] = 1
    #     else:
    #         item_dict[line['item_category']][line['item_id']] += 1
    # print item_dict

    lines = fileHandler.readFile(settings.USER_FILE, 100000)

    user_dict = {}
    item_buy_dict = {}

    for line in lines:
        if line['user_id'] not in user_dict:
            user_dict[line['user_id']] = {}
        if line['item_category'] not in user_dict[line['user_id']]:
            user_dict[line['user_id']][line['item_category']] = [0, 1]
        else:
            user_dict[line['user_id']][line['item_category']][1] += 1
        if line['behavior_type'] == '4':
            user_dict[line['user_id']][line['item_category']][0] += 1
            if line['item_id'] not in item_buy_dict:
                item_buy_dict[line['item_category']] = {}
                item_buy_dict[line['item_category']][line['item_id']] = 1
            else:
                item_buy_dict[line['item_category']][line['item_id']] += 1

    # item_buy_dict['13737']['333333333'] = 1

    for itemcat in item_buy_dict:
        item_buy_dict[itemcat] = sorted(item_buy_dict[itemcat].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
    return user_dict, item_buy_dict

if __name__ == '__main__':
    build_user_feature_vector()