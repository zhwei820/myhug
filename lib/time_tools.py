# coding=utf-8

import datetime

def datetime2timestamp(dt, convert_to_utc=False):
    ''' Converts a datetime object to UNIX timestamp in milliseconds. '''
    if isinstance(dt, datetime.datetime):
        if convert_to_utc: # 是否转化为UTC时间
            dt = dt + datetime.timedelta(hours=-8) # 中国默认时区
        timestamp = total_seconds(dt - EPOCH)
        return long(timestamp)
    return dt

def timestamp2datetime(timestamp, convert_to_local=False):
    ''' Converts UNIX timestamp to a datetime object. '''
    if isinstance(timestamp, (int, long, float)):
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        if convert_to_local: # 是否转化为本地时间
            dt = dt + datetime.timedelta(hours=8) # 中国默认时区
        return dt
    return timestamp

def timestamp_utc_now():
    return datetime2timestamp(datetime.datetime.utcnow())

def timestamp_now():
    return datetime2timestamp(datetime.datetime.now())

#pip install python-dateutil
from dateutil import tz
from dateutil.tz import tzlocal

# get local time zone name
print(datetime.datetime.now(tzlocal()).tzname())

# UTC Zone
from_zone = tz.gettz('UTC')
# China Zone
to_zone = tz.gettz('CST')

utc = datetime.datetime.utcnow()
print(utc)

# Tell the datetime object that it's in UTC time zone
utc = utc.replace(tzinfo=from_zone)

# Convert time zone
local = utc.astimezone(to_zone)
print (datetime.datetime.strftime(local, "%Y-%m-%d %H:%M:%S"))
