import datetime
import time
# import json


# 获取时间戳
def get_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S')
