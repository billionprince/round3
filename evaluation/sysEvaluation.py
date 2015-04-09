from util import fileHandler, userHandler
import settings

def sysTest(recommendation_dict):
    gd_truth = userHandler.get_test_data_from_test_table('testdata')
    # user_buy_item = userHandler.get_all_userid_and_itemid_distinct(4, 'trainbuydata') # list of item each user buy

    num_hit = 0 #num of hit, true positive
    num_recommend = 0 # num of recommendation, true positive+false positive
    num_real_buy = 0 # num of real buy, true positive+false negative
    F_measure = 0
    hit_usr = 0

    for ui in recommendation_dict:
        num_recommend += len(recommendation_dict[ui])

    for ui in gd_truth:
        num_real_buy += len(gd_truth[ui])
        if ui in recommendation_dict:
            hit_usr += 1
            for ti in gd_truth[ui]:
                if ti in recommendation_dict[ui]:
                    num_hit += 1

    precision = 1.0 * num_hit / num_recommend
    recall = 1.0 * num_hit / num_real_buy
    F_measure = 2.0 * precision * recall / (precision + recall)
    print 'precision =', precision
    print 'recall=', recall
    print 'F_measure=', F_measure
    print 'total recommendation =',  num_recommend
    print 'hit_item =', num_hit
    print 'hit_user =', hit_usr
    # print 'pre_cnt =', pre_cnt
    print 'num of gdtruth =', num_real_buy
    # print 'pre_user =', pre_user
    return F_measure
