from paho.mqtt import client as mqtt_client
import multiprocessing
import json
import os
from utils.utils import *


class MqtterProcess(multiprocessing.Process):
    def __init__(self, host, port, _flag, queue):
        super().__init__()
        self.broker = host
        self.port = port
        self._flag = _flag
        self.queue = queue
        self.keepalive = 60  # 与代理通信之间允许的最长时间段（以秒为单位）
        self.client = None
        with open("./static/deviceInform.json", 'r') as f:
            self.deviceInform = json.load(f)
        with open("./static/config.json", 'r') as f2:
            self.params = json.load(f2)
        self.selfTopic = '/client/{0}/{1}'.format(self.deviceInform['devType'], self.deviceInform['deviceId'])

    def run(self):
        self.client = self.connect_mqtt()
        self.client.loop_start()
        while True:
            if self._flag.value and ~self.queue.empty():
                data = self.queue.get()
                self.client.publish('/client/showdata', data, 2)

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            # 响应状态码为0表示连接成功
            if rc == 0:
                inform = json.dumps({
                    'timestamp': '',
                    'message': 'Device online',
                    'data': self._parse_inform()
                })
                self.publish('/client/online', inform)
                print("Connection returned with result code:" + str(rc))
            else:
                print("连接失败！")

        def on_message(client, userdata, msg):
            print("Received message, topic:" + msg.topic + ' and payload:' + str(msg.payload))
            msg_topic = msg.topic
            msg_payload = json.loads(msg.payload)
            if msg_topic.endswith('/reboot'):
                self._res_reboot(client, userdata, msg)
            if msg_topic.endswith('/update'):
                self._res_update(client, userdata, msg)
            if msg_topic.endswith('/add'):
                # 预留接口
                pass
            if msg_topic.endswith('/remove'):
                # 预留接口
                pass
            if msg_topic.endswith('/showdata'):
                if self._flag.value:
                    self._stop()
                self._start()
            if msg_topic.endswith('/stop'):
                if self._flag.value:
                    self._stop()

        client = mqtt_client.Client()
        # # 设置账号密码（如果需要的话）
        # client.username_pw_set('username', 'password')
        client.on_connect = on_connect
        msg = json.dumps({
            'timestamp': '',
            'message': 'Device offline',
            'data': self._parse_inform()
        })
        # client.will_set(self.topic, payload=msg)
        client.connect(self.broker, self.port, self.keepalive)
        client.on_message = on_message
        client.subscribe('/broker/request/#')
        client.subscribe('/broker/{0}/{1}/#'.format(self.deviceInform['devType'], self.deviceInform['deviceId']))
        return client

    def subscribe(self, topic):
        self.client.subscribe(topic)  # 命令的Qos设置为0

    def publish(self, topic, msg):
        self.client.publish(topic, payload=msg)

    def _parse_inform(self):
        inform = json.dumps({
            'deviceId': self.deviceInform['deviceId'],
            'devType': self.deviceInform['devType'],
            'stat': self.deviceInform['stat'],
            'params': self.params,
            'position': self.deviceInform['position'],
            'ip': self.deviceInform['ip']
        })
        return inform

    # _res_showdata()
    def _start(self):
        self._flag.value = True

    def _stop(self):
        self._flag.value = False

    def _res_update(self, client, userdata, msg):
        inform = json.dumps({'message': 'Acoustic8 received the request for changing params'})
        params = json.loads(msg.payload)['data']
        with open("./static/config.json", "w") as f:
            json.dump(params, f)
        self.client.publish(self.selfTopic + "/update", payload=inform)

    def _res_reboot(self, client, userdata, msg):
        inform = json.dumps({'message': 'Acoustic8 received the request for rebooting'})
        self.client.publish(self.selfTopic + "/update", payload=inform)
        # 端设备回应broker已经收到消息，下面需要执行一个指令来重启设备
        inform = json.dumps({
            'timestamp': '',
            'message': 'Device offline',
            'data': self._parse_inform()
        })
        client.publish('/client/offline', inform)
        os.system("sudo reboot")