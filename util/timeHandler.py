import datetime

def sub_days_of_two_time(time1, time2):
    if not isinstance(time1, basestring) or not isinstance(time2, basestring):
        raise Exception('parameters of function "sub_days_of_two_time" show be string')
    d1 = datetime.datetime.strptime(time1.split(' ')[0], '%Y-%m-%d')
    d2 = datetime.datetime.strptime(time2.split(' ')[0], '%Y-%m-%d')
    return (d2 - d1).days

def sub_days(time, days):
    d = datetime.datetime.strptime(time.split(' ')[0], '%Y-%m-%d')
    return (d - datetime.timedelta(days)).strftime('%Y-%m-%d %H')