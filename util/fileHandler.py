import codecs
import os.path

def readFile(path, lineNum=None):
    path = os.path.abspath(path)
    print path
    if not os.path.isfile(path):
        raise ValueError('file path is invalid')
    with codecs.open(path, 'rb', 'utf-8') as fin:
        if lineNum:
            lines = [next(fin).strip('\n') for x in xrange(lineNum)]
        else:
            lines = fin.readlines()
    rec, title = [], lines[0].split(',')
    for line in lines[1:]:
        rec.append({title[sp]: field for sp, field in enumerate(line.split(','))})
    return rec

def writeFile(path, lines):
    path = os.path.abspath(path)
    with codecs.open(path, 'wb', 'utf-8') as fout:
        fout.write(lines)
    return True