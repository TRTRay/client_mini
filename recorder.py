import time
import pyaudio
import multiprocessing
import json


class RecorderProcess(multiprocessing.Process):
    def __init__(self,_flag,queue):
        super().__init__()
        config=json.load(open("./static/config.json", 'r'))
        self.RECORDER_INDEX=config['recorderIndex']
        self.CHUNK = 1024
        self.RECORDER_WIDTH = 2
        self.CHANNELS = config['recorderChannals']
        self.RATE = config['sampleRate']
        self._flag=_flag
        self.queue=queue

    def run(self):
        print('----------开始录制----------')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.RECORDER_WIDTH),
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK,
                        input_device_index=self.RECORDER_INDEX)
        while self._flag.value:
            data = stream.read(self.CHUNK)
            self.queue.put(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print('----------停止录制----------')