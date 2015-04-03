from util import fileHandler
import settings

def sysTest(recommendation_dict):
    lines = fileHandler.readFile(settings.USER_FILE, 10000)

    num_hit = 1 #num of hit, true positive
    num_recommend = 1 # num of recommendation, true positive+false positive
    num_real_buy = 1 # num of real buy, true positive+false negative

    for usr in recommendation_dict:
        num_recommend += len(recommendation_dict[usr])
    for line in lines:
        num_real_buy += 1
        userid = line['user_id']
        if userid in recommendation_dict:
            itemid = line['item_id']
            if itemid in recommendation_dict[userid]:
                num_hit += 1
    precision = 1.0 * num_hit / num_recommend
    recall = 1.0 * num_hit / num_real_buy
    F_measure = 2.0 * precision * recall / (precision + recall)
    print 'precision =', precision
    print 'recall=', recall
    print 'F_measure=', F_measure
    return F_measure

