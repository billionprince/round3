from util import fileHandler
import settings

def sysTest(recommendation_dict):
    lines = fileHandler.readFile(settings.USER_FILE, 10000)

    cnt0 = 0 #num of hit
    cnt1 = 0 # num of recommendation
    cnt2 = 0 # num of real buy

    for usr in recommendation_dict:
        cnt1 += len(recommendation_dict[usr])
    for line in lines:
        cnt2 += 1
        userid = line['user_id']
        if userid in recommendation_dict:
            itemid = line['item_id']
            if itemid in recommendation_dict[userid]:
                cnt0 += 1
    precision = cnt0 / cnt1
    recall = cnt0 / cnt2
    F_measure = 2 * precision * recall / (precision + recall)
    print F_measure
    return F_measure