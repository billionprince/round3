import codecs
import os
import settings
import csv

def readCsvFile(path, val_type, lineNum=None):
    path = os.path.abspath(path)
    print path
    if not os.path.isfile(path):
        raise ValueError('file path is invalid')
    with codecs.open(path, 'rb', 'utf-8') as fin:
        if lineNum:
            lines = [next(fin).strip('\n') for x in xrange(lineNum)]
        else:
            lines = [line.strip('\n') for line in fin.readlines()]
    rec, title = {}, (lines[0].strip('\r')).split(',')
    # print title
    for line in lines[1:]:
        tp_line = (line.strip('\r')).split(',')
        # print tp_line
        if str(tp_line[0]) not in rec:
            rec[str(tp_line[0])] = []
        if len(tp_line) == 2:
            rec[str(tp_line[0])].append(tp_line[1])
        else:
            tp_lst = []
            for i in range(1, len(tp_line)):
                if val_type[i] == 'str':
                    tp_lst.append(str(tp_line[i]))
                if val_type[i] == 'int':
                    # print type(tp_line[i])
                    # print tp_line[i]
                    tp_lst.append(int(tp_line[i]))
            rec[str(tp_line[0])].append(tp_lst)

    return rec

def writeFile(path, lines):
    path = os.path.abspath(path)
    with codecs.open(path, 'wb', 'utf-8') as fout:
        fout.write(lines)
    return True

def writeCsvFile(path, lines, title):
    path = os.path.abspath(path)
    with codecs.open(path, 'wb', 'utf-8') as fout:
        writer = csv.writer(fout)
        writer.writerow(title)
        for uid in lines:
            # rows = [[uid, tid] for tid in set(lines[uid])]
            # writer.writerows(rows)
            for ui in lines[uid]:
                # print ui
                rows = [uid]
                if isinstance(ui, list):
                    for uj in ui:
                        rows.append(uj)
                else:
                    rows.append(ui)
                # print rows
                writer.writerows([rows])
            # break
    return True