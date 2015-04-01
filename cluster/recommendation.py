import csv

def item_recommendation(user_classlabel, user_dict, item_type_dict, item_type_idx):
    csvfile = open('tianchi_mobile_recommend_train_user.csv')
    #user_id item_id behavior_type user_geohash item_category time
    csvfile.readline()
       
    reader = csv.reader(csvfile)
    
    class_num = len(user_classlabel)
    
    userclass_item_cnt = [[0 for col in range(len(item_type_dict)+1)] for row in range(class_num)] # cnt of each category of item of each user class
     
    for c in reader:
        user_class = user_classlabel[user_dict[c[0]][4]]
        if c[4] in item_type_dict and user_class != -1:
            if c[2] == '4':
                userclass_item_cnt[user_class][item_type_dict[c[4]]] += 1
            

    csvfile.close()

    
    for i in range(class_num):
        final_itemlist = []
        for j in range(1, len(item_type_dict) + 1):
            final_itemlist.append((j, userclass_item_cnt[i][j]))
        final_itemlist.sort(key=lambda x:x[1], reverse=True)
        print final_itemlist
        for j in range(10): # for each user class, recommend 10 item categories
            print item_type_idx[final_itemlist[j][0]]
            