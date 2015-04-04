import codecs
import os
import settings
import csv

def readFile(path, lineNum=None):
    path = os.path.join(os.path.dirname(settings.__file__), path)
    if not os.path.isfile(path):
        raise ValueError('file path is invalid')
    with codecs.open(path, 'rb', 'utf-8') as fin:
        if lineNum:
            lines = [next(fin).strip('\n') for x in xrange(lineNum)]
        else:
            lines = [line.strip('\n') for line in fin.readlines()]
    rec, title = [], lines[0].split(',')
    for line in lines[1:]:
        rec.append({title[sp]: field for sp, field in enumerate(line.split(','))})
    return rec

def writeFile(path, lines):
    path = os.path.abspath(path)
    with codecs.open(path, 'wb', 'utf-8') as fout:
        fout.write(lines)
    return True

def writeCsvFile(path, lines):
    path = os.path.abspath(path)
    title = ['user_id', 'item_id']
    with codecs.open(path, 'wb', 'utf-8') as fout:
        writer = csv.writer(fout)
        writer.writerow(title)
        for uid in lines:
            rows = [[uid, tid] for tid in set(lines[uid])]
            writer.writerows(rows)
    return True