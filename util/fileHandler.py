import codecs
import os
import settings
import csv

def readCsvFile(path, val_type, lineNum=None):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise ValueError('file path is invalid')
    with codecs.open(path, 'rb', 'utf-8') as fin:
        if lineNum:
            lines = [next(fin).strip('\n') for x in xrange(lineNum)]
        else:
            lines = [line.strip('\n') for line in fin.readlines()]
    rec, title = {}, (lines[0].strip('\r')).split(',')
    for line in lines[1:]:
        tp_line = (line.strip('\r')).split(',')
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
                    tp_lst.append(int(tp_line[i]))
            rec[str(tp_line[0])].append(tp_lst)

    return rec

def writeFile(path, lines):
    path = os.path.abspath(path)
    with codecs.open(path, 'wb', 'utf-8') as fout:
        fout.write(lines)
    return True

def writeCsvFile(path=os.path.join(os.path.dirname(settings.__file__), settings.OUTPUT_CSV), lines=[], title=['user_id', 'item_id']):
    path = os.path.abspath(path)
    with codecs.open(path, 'wb', 'utf-8') as fout:
        writer = csv.writer(fout)
        writer.writerow(title)
        if isinstance(lines, dict):
            rows = [[k, v] for k in lines for v in lines[k] if isinstance(lines[k], list)]
            rows += [[k, lines[k]] for k in lines if not isinstance(lines[k], list)]
            writer.writerows([rows])
        elif isinstance(lines, list):
            writer.writerows(lines)
        else:
            raise Exception('writeCsvFile, lines type is invalid')