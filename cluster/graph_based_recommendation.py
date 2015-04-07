import settings
import os
import sqlite3
from util import fileHandler, userHandler, itemHandler

TEMP_FILE_CATEGORY_PAIR = 'cluster/category_pair.csv'
TEMP_FILE_HOT_ITEM = 'cluster/hot_item.csv'
DB_PATH = os.path.join(os.path.dirname(settings.__file__), settings.DB_NAME)
CONN = sqlite3.connect(DB_PATH)
USERLIST = ['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']
IMTELIST = ['item_id', 'item_geohash', 'item_category']

def recommendation(cat_sim_thr, user_sim_thr, min_cat_sz, min_cat_thr, min_rec_per_cat):
    # item_id = itemHandler.get_all_itemid() # total:314694
    # n_item = userHandler.get_item_category_count_in_userlist() # total category:120236

    # cat_buy_times = userHandler.get_item_buy_category_count_in_userlist()
    # item_buy_times = userHandler.get_item_buy_times_in_userlist()
    # user_buy_list = userHandler.get_all_user_buy_items()
    # user_prefer = {}
    # item_overlap_times = {}

## =================150406 BEGIN================= ##

    recommendation_dict = {}
    cat_overlap_dict = {}
    # # preprocess category pair into csv to speed up
    # cat_overlap_dict_pre = get_buy_category_pair(table='traindata')
    # for ci in cat_overlap_dict_pre:
    # #     print cat_overlap_dict_pre[ci]
    # #     break
    #     if len(cat_overlap_dict_pre[ci]) > min_cat_sz:
    #         cat_overlap_dict[ci] = cat_overlap_dict_pre[ci]
    # fileHandler.writeCsvFile(TEMP_FILE_CATEGORY_PAIR, cat_overlap_dict, ['item_id1', 'item_id2'])
    # read preprocessed csv file of category pair
    cat_overlap_dict = fileHandler.readCsvFile(TEMP_FILE_CATEGORY_PAIR, ['str', 'str'], lineNum=None)
    # for ci in cat_overlap_dict:
    #     print ci
    # print 'ok'

    # # preprocess hot item of each category into csv to speed up
    # cat_hot_item = get_buy_item_count_by_all_category()
    #
    # fileHandler.writeCsvFile(TEMP_FILE_HOT_ITEM, cat_hot_item, ['item_category', 'item_id', 'count'])

    # print 'end'
    # read preprocessed csv file of category pair
    cat_hot_item = fileHandler.readCsvFile(TEMP_FILE_HOT_ITEM, ['str', 'str', 'int'], lineNum=None)
    # item category similarityval_type
    # for ci in cat_hot_item:
    #     print cat_hot_item[ci]
    #     break
    cat_similarity = {}
    cat_neighbor = {}
    user_similarity = {}

    print 'end'

    for ci in cat_overlap_dict:
        # print cat_overlap_dict[ci]
        # break
        cat_hot_item[ci].sort(lambda x, y: cmp(x[1], y[1]), reverse = True)
        n_ci = len(cat_overlap_dict[ci])
        # print cat_hot_item[ci]
        # break
        cat_similarity[ci] = {}
        cat_neighbor[ci] = []
        # cnt = 0
        for cj in cat_overlap_dict:
            # print cat_overlap_dict[cj]
            n_cj = len(cat_overlap_dict[cj])
            # print cat_overlap_dict[ci].count(cj)
            # print cat_overlap_dict[ci]

            cat_similarity[ci][cj] = cat_overlap_dict[ci].count(cj) * 1.0 / (1.0 * (n_ci + n_cj))
            # print n_ci
            # print n_cj
            # print cat_overlap_dict[ci].count(cj)
            # print cat_similarity[ci][cj]
            if cat_similarity[ci][cj] > cat_sim_thr:
                # cnt += 1
                cat_neighbor[ci].append(cj)
                # print cat_similarity[ci][cj]
        # print cat_overlap_dict[ci].count('1169')
        # break
        # print cnt
        # break
    print 'end cat neighbour calculation'
    # print cat_neighbor

    #user recommendation
    user_buy_category_dict = {}
    user_id = userHandler.get_userid_buy_behavior_num() # >=2 times, 129 user
    # print len(user_id)
    for ui in user_id:
        print 'ui=', ui
        recommendation_dict[ui] = []
        user_similarity[ui] = {}
        user_buy_category_dict = dict(user_buy_category_dict, **userHandler.get_user_buy_item_categories_by_userid(ui))
        # print user_buy_category_dict
        # break
        if len(user_buy_category_dict[ui]) <= min_cat_thr:
            continue
        for ci in user_buy_category_dict[ui]:
            # recommend hot item in similar category but the user haven't bought
            if ci not in cat_neighbor:
                continue
            for cj in cat_neighbor[ci]:
                if cj not in user_buy_category_dict[ui]:
                    for ti in range(min(min_rec_per_cat, len(cat_hot_item[ci]))):
                        if cat_hot_item[ci][ti] not in recommendation_dict[ui]:
                            recommendation_dict[ui].append(cat_hot_item[ci][ti][0])
            # recommend hot item in the category the user bought many times
            for ti in range(min(min_rec_per_cat, len(cat_hot_item[ci]))):
                if cat_hot_item[ci][ti] not in recommendation_dict[ui]:
                    recommendation_dict[ui].append(cat_hot_item[ci][ti][0])

    # recommend hot item the neighbor user bought many times
    for ui in user_id:
        for uj in user_id:
            if len(user_buy_category_dict[uj]) <= min_cat_thr:
                continue
            same_cat_lst = list(set(user_buy_category_dict[ui]).intersection(set(user_buy_category_dict[uj])))
            # print 'len=', len(same_cat_lst)
            # print len(user_buy_category_dict[ui])
            # print len(user_buy_category_dict[uj])
            user_similarity[ui][uj] = 1.0 * len(same_cat_lst) / (1.0 * (len(user_buy_category_dict[ui]) + len(user_buy_category_dict[uj])))
            # print user_similarity[ui][uj]
            if user_similarity[ui][uj] > user_sim_thr:
                for ci in same_cat_lst:
                    # print 'l=', ci
                    for ti in range(min(min_rec_per_cat, len(cat_hot_item[ci]))):
                        # print ti
                        if cat_hot_item[ci][ti] not in recommendation_dict[ui]:
                            recommendation_dict[ui].append(cat_hot_item[ci][ti][0])
                        print recommendation_dict[ui]
            # print 'pls'
    # print type(recommendation_dict)

## =================150406 END================= ##

    # # item similarity
    # item_overlap_dict = get_buy_item_pair_by_userid()
    # item_similarity = {}
    # nci = {}
    #
    # for ti in cat_overlap_dict:
    #     n_ti = len(cat_overlap_dict[ci])
    #     item_similarity[ci] = {}
    #     for cj in cat_overlap_dict:
    #         n_cj = len(cat_overlap_dict[cj])
    #         cat_similarity[ci][cj] = cat_overlap_dict[ci].count(cj) * 1.0
    #         cat_similarity[ci][cj] /= (1.0 * (n_ci + n_cj))
    #         if cat_similarity[ci][cj] > 0:
    #             print cat_similarity[ci][cj]
    #     break

    # for ui in range(len(user_id)):
    #     item_pair = get_buy_item_pair_by_userid(user_id[ui])
    #     print item_pair
    #     break
    #     for ti in range(len(user_buy_list[user_id[ui]])):
    #         if user_buy_list[user_id[ui]][ti] not in item_overlap_times:
    #             item_overlap_times[user_buy_list[user_id[ui]][ti]] = {}
    #
    #         ti_cat = userHandler.get_item_category_by_itemid(user_buy_list[user_id[ui]][ti])
    #         if ti_cat[0] not in cat_overlap_times:
    #             cat_overlap_times[ti_cat[0]] = {}
    #
    #         for tj in range(len(user_buy_list[user_id[ui]])):
    #             if ti == tj:
    #                 continue
    #             if user_buy_list[user_id[ui]][tj] not in item_overlap_times[user_buy_list[user_id[ui]][ti]]:
    #                 item_overlap_times[user_buy_list[user_id[ui]][ti]][user_buy_list[user_id[ui]][tj]] = 1
    #             else:
    #                 item_overlap_times[user_buy_list[user_id[ui]][ti]][user_buy_list[user_id[ui]][tj]] += 1
    #
    #             tj_cat = userHandler.get_item_category_by_itemid(user_buy_list[user_id[ui]][tj])
    #             if tj_cat[0] not in cat_overlap_times[ti_cat[0]]:
    #                 cat_overlap_times[ti_cat[0]][tj_cat[0]] = 1
    #             else:
    #                 cat_overlap_times[ti_cat[0]][tj_cat[0]] += 1
    #
    # for ci in cat_overlap_times:
    #     ci_buy_times = cat_buy_times[ci]
    #     for cj in cat_overlap_times[ci]:
    #         if cat_overlap_times[ci] > 0 and cat_overlap_times[cj] > 0:
    #             cj_buy_times = cat_buy_times[cj]
    #             cat_overlap_times[ci][cj] = 1.0 * cat_overlap_times[ci][cj] / (1.0 * ci_buy_times * cj_buy_times)
    #         else:
    #             cat_overlap_times[ci][cj] = 0
    #     cat_overlap_times[ci] = sorted(cat_overlap_times[ci].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
    #     print cat_overlap_times
    #
    # for ui in range(len(user_id)):
    #     cat_list[ui] = userHandler.get_user_buy_item_categories_by_userid(user_id[ui])


        # if len(buy_list[ui]) > 50:
        #     user_prefer[ui] = []
        #     for ti in range(len(buy_list[ui])):
        #         if buy_list[ui][ti] not in user_prefer[ui]:
        #             tp_list = userHandler.get_item_category_by_itemid(buy_list[ui][ti])
        #             user_prefer[ui].append(tp_list[0])


    # for ti in item_overlap_times:
    #     for tj in item_overlap_times[ti]:
    #         if item_buy_times[ti] > 0 and item_buy_times[tj] > 0:
    #             print item_buy_times[ti]
    #             print item_buy_times[tj]
    #             item_overlap_times[ti][tj] = 1.0 * item_overlap_times[ti][tj] / (1.0 * item_buy_times[ti] * item_buy_times[tj])
    #         else:
    #             item_overlap_times[ti][tj] = 0
    #     item_overlap_times[ti] = sorted(item_overlap_times[ti].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
    #
    # print item_overlap_times





    # user_dict = {}
    # userid_idx = {}
    # userid_str = []
    # user_mtx = {}
    #
    # itemid_idx = {}
    #
    # i = 0
    # n_user = len(user_id)
    # n_item = 0
    #
    # for useri in user_id:
    #     user_mtx[useri] = {}
    #     for userj in user_id:
    #         if useri != userj:
    #             same_item_cat = userHandler.get_buy_item_categories_of_mulitple_users_by_userid([useri, userj])
    #             user_mtx[useri][userj] = len(same_item_cat)
    #         else:
    #             user_mtx[useri][userj] = 0
    #
    #     user_mtx[useri] = sorted(user_mtx[useri].items(), lambda x, y: cmp(x[1], y[1]), reverse = True)




    # for useri in user_id:
    #     itemlist = userHandler.get_user_buy_item_categories_by_userid(useri)
    #     userid_idx[useri] = i
    #     userid_str.append(useri)
    #     i += 1
        # for j in range(itemlist):
        #     if itemlist[j] not in item_id:
        #         item_id.append(itemlist[j])
        #         itemid_idx[itemlist[j]] = n_item
        #         n_item += 1
        #     tp_itemidx = itemid_idx[itemlist[j]]
        #     sp_mtx[i - 1][n_user + n_item - 1] = 1



    # for i in range(n_user):
    #     for j in range(n_user):
    #         if i == j:
    #             continue
    #         if userHandler.get_user_geo_by_uid(userid_str[i]) == userHandler.get_user_geo_by_uid(userid_str[j]):
    #             print 'here'
    #             break


        # itemlist = userHandler.get_user_buy_items_by_userid(useri)
        # if len(itemlist) == 0:
        #     print 'here'
        #     break



    # get_user_buy_item_by_userid(uid)
    # lines = fileHandler.readFile(settings.USER_FILE, 10000)
    #
    # sp_mtx = []
    # user_label = {}
    # item_label = {}
    # item_cat_label = {}
    #
    # for line in lines:
    #     if line['user_id'] not in user_label:
    #         user_label[line['user_id']] = len(user_label)
    #
    #     if line['item_id'] not in item_label:
    #         item_label[line['item_id']] = len(item_label)
    #
    #     if line['item_category'] not in user_label:
    #         item_cat_label[line['item_category']] = len(item_cat_label)

    return recommendation_dict

def get_buy_item_pair_by_userid(uid, table='traindata'):
    cursor = CONN.cursor()
    int_uid = uid
    if not isinstance(uid, int):
        int_uid = int(int_uid)
    q = 'select A.user_id, A.item_id, B.item_id from userlist A, userlist B '
    q += 'where A.user_id = B.user_id and a.item_id != b.item_id and a.behavior_type=4 and b.behavior_type=4'
    cursor.execute(q % table)
    lines = cursor.fetchall()
    rec = {}
    for line in lines:
        if str(line[0]) not in rec:
            rec[str(line[0])] = [[str(line[1]), str(line[2])]]
        else:
            rec[str(line[0])].append([str(line[1]), str(line[2])])
    cursor.close()
    return rec

def get_buy_category_pair(table='traindata'):
    cursor = CONN.cursor()
    q = 'select A.item_category, B.item_category from %s A, %s B '
    q += 'where A.user_id = B.user_id and a.item_category != b.item_category and a.behavior_type=4 and b.behavior_type=4'
    cursor.execute(q % (table, table))
    lines = cursor.fetchall()
    rec = {}
    for line in lines:
        if str(line[0]) not in rec:
            rec[str(line[0])] = [str(line[1])]
        else:
            rec[str(line[0])].append(str(line[1]))
    cursor.close()
    return rec

# def get_buy_category_pair_selected(min_item_thr, table='traindata'):
#     cursor = CONN.cursor()
#     q = 'select A.item_category, B.item_category from %s A, %s B '
#     q += 'group by A.item_category having A.user_id = B.user_id '
#     q += 'and a.item_category != b.item_category and a.behavior_type=4 and b.behavior_type=4 and count(*) > %d'
#     cursor.execute(q % (table, table, min_item_thr))
#     lines = cursor.fetchall()
#     rec = {}
#     for line in lines:
#         if str(line[0]) not in rec:
#             rec[str(line[0])] = [[str(line[1])]]
#         else:
#             rec[str(line[0])].append([str(line[1])])
#     cursor.close()
#     return rec

def get_buy_item_count_by_category(cid, table='traindata'):
    cursor = CONN.cursor()
    int_cid = cid
    if not isinstance(cid, int):
        int_cid = int(int_cid)
    q = 'select item_id, count(*) from %s '
    q += 'where item_category=%s and behavior_type=4 group by item_id'
    # q = 'select item_category, item_id, count(*) from userlist group by item_id '
    # q += 'having item_category=%s and behavior_type=4'
    cursor.execute(q % (table, int_cid))
    lines = cursor.fetchall()
    rec = []
    for line in lines:
        rec.append([str(line[0]), int(line[1])])
    cursor.close()
    # print rec
    return rec

def get_buy_item_count_by_all_category(table='traindata'):
    cursor = CONN.cursor()
    q = 'select item_category, item_id, count(*) from %s '
    q += 'where behavior_type=4 group by item_id'
    # q = 'select item_category, item_id, count(*) from userlist group by item_id '
    # q += 'having item_category=%s and behavior_type=4'
    cursor.execute(q % table)
    lines = cursor.fetchall()
    rec = {}
    for line in lines:
        if line[0] not in rec:
            rec[line[0]] = []
        rec[line[0]].append([str(line[1]), int(line[2])])
    cursor.close()
    # print rec
    return rec

# def write_tempfile_dict(path, lines):
#     path = os.path.abspath(path)
#     # title = ['item_id1', 'item_id2']
#     with codecs.open(path, 'wb', 'utf-8') as fout:
#         writer = csv.writer(fout)
#         # writer.writerow(title)
#         for uid in lines:
#             rows = [uid]
#             for i in lines[uid][0]:
#                 rows.append(str(i))
#             writer.writerows([rows])
#     return True

# def read_tempfile_dict(path, lineNum=None):
#     path = os.path.abspath(path)
#     print path
#     if not os.path.isfile(path):
#         raise ValueError('file path is invalid')
#     with codecs.open(path, 'rb', 'utf-8') as fin:
#         if lineNum:
#             lines = [next(fin).strip('\n') for x in xrange(lineNum)]
#         else:
#             lines = [line.strip('\n') for line in fin.readlines()]
#     rec = {}
#     for line in lines:
#         tp_line = (line.strip('\r')).split(',')
#         if str(tp_line[0]) not in rec:
#             rec[str(tp_line[0])] = []
#         if len(tp_line) > 2:
#             tp_lst = [tp_line[1]]
#             for i in tp_line[2:]:
#                 tp_lst.append(int(i))
#             rec[str(tp_line[0])].append(tp_lst)
#         else:
#             rec[str(tp_line[0])].append(tp_line[1])
#
#     return rec



if __name__ == '__main__':
    recommendation(cat_sim_thr=0.001, min_cat_sz=30, min_cat_thr=2, min_rec_per_cat=2)
    # dict = get_buy_item_count_by_all_category()
    # for di in dict:
    #     print dict[di]