import multiprocessing
import ctypes

from mqtter import MqtterProcess
from player import PlayerProcess
from recorder import RecorderProcess


MQTT_HOST = '182.92.152.209'  # mqtt代理服务器地址
MQTT_PORT = 1883

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    '''运行标志'''
    _FLAG = multiprocessing.Value(ctypes.c_bool, False)
    '''数据队列'''
    DATA_QUEUE = multiprocessing.Queue()

    mqtter_process = MqtterProcess(MQTT_HOST, MQTT_PORT, _FLAG, DATA_QUEUE)
    mqtter_process.start()

    while True:
        if _FLAG.value:
            print("----------启动中----------")
            player_process = PlayerProcess(_FLAG)
            recoder_process = RecorderProcess(_FLAG, DATA_QUEUE)
            player_process.start()
            recoder_process.start()
            while _FLAG.value:
                pass
            player_process.join(0.5)
            recoder_process.join(0.5)
            # python3.10取消了Queue.queue.clear()方法，假如queue非空的话消耗queue
            while not DATA_QUEUE.empty():
                DATA_QUEUE.get()
            print("----------已停止----------")