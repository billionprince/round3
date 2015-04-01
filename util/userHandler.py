from util import fileHandler
import settings

def build_user_feature_vector():
    lines = fileHandler.readFile(settings.USER_FILE, 100)

    usr_dict = {}
     
    for line in lines:
        username = line['user_id']
        if username not in usr_dict:
            usr_dict[username] = [0., 0., 0., 0.]
        usr_dict[username][int(line['behavior_type'])-1] += 1

    for usr in usr_dict:
        tot = sum(usr_dict[usr][:3])
        usr_dict[usr] = [val/tot for val in usr_dict[usr]]

    return usr_dict