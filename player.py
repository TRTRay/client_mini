import sys
import pyaudio
import wave
import os
import multiprocessing
import json

BASEPATH = sys.path[0].replace("\\", "/")
DATAPATH = BASEPATH + '/static'
if not os.path.exists(DATAPATH):
    os.makedirs(DATAPATH)


class PlayerProcess(multiprocessing.Process):
    def __init__(self, _flag, filename='Tchirp.wav'):
        super().__init__()
        config = json.load(open("./static/config.json", 'r'))
        self.CHUNK = 1024
        self._input = DATAPATH + '/' + filename
        self._flag = _flag
        self.PLAYER_INDEX = config['playerIndex']

    def run(self):
        print('----------开始播放----------')
        while self._flag.value:
            wf = wave.open(self._input, 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            input_device_index=self.PLAYER_INDEX)
            while self._flag.value:
                data = wf.readframes(self.CHUNK)
                if data == b'':
                    break
                stream.write(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            wf.close()
        print('----------结束播放----------')