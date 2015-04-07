from util import fileHandler, userHandler
import settings

def sysTest(recommendation_dict):
    gd_truth = userHandler.get_test_data_from_test_table('testdata')
    num_hit = 1 #num of hit, true positive
    num_recommend = 1 # num of recommendation, true positive+false positive
    num_real_buy = 1 # num of real buy, true positive+false negative

    for ui in recommendation_dict:
        num_recommend += len(recommendation_dict[ui])
    for ui in gd_truth:
        num_real_buy += len(gd_truth[ui])
        if ui in recommendation_dict:
            for ti in gd_truth[ui]:
                if ti in recommendation_dict[ui]:
                    num_hit += 1
    # print num_real_buy
    precision = 1.0 * num_hit / num_recommend
    recall = 1.0 * num_hit / num_real_buy
    F_measure = 2.0 * precision * recall / (precision + recall)
    print 'precision =', precision
    print 'recall=', recall
    print 'F_measure=', F_measure
    print 'recom =',  num_recommend
    print 'hit =', num_hit
    print 'gdtruth =', num_real_buy
    return F_measure
