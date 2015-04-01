from util import fileHandler
import settings

def item_input():
    lines = fileHandler.readFile(settings.ITEM_FILE)
    return ({}, {}, {})
#     item_dict = {}
#     item_type_cnt = {}
#     item_type_dict = {}
#     item_type_idx = {}
# # item_id,item_geohash,item_category
#     for line in lines:
#         item_dict[line['item_id']] = [c[1], c[2]]
#         if c[2] not in item_type_cnt:
#             item_type_cnt[c[2]] = 1
#             item_type_dict[c[2]] = len(item_type_cnt)
#             item_type_idx[len(item_type_cnt)] = c[2]
#         else:
#             item_type_cnt[c[2]] += 1
#
#     return item_dict, item_type_dict, item_type_idx

def get_item_type():
    return []

def get_items(lineNum=None):
    lines = []
    if lineNum:
        lines = fileHandler.readFile(settings.ITEM_FILE, lineNum)
    else:
        lines = fileHandler.readFile(settings.ITEM_FILE, lineNum)
    return lines

