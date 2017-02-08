#!/usr/bin/python3
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from naniologger import logger
import json
from BluetoothHandle import *
import threading

app = Flask("nanio-lightshow")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def hsi(btHandle, data):
    if 'hue' in data \
        and 'saturation' in data \
        and 'intensity' in data:
        h = float(data['hue'])
        s = float(data['saturation'])
        i = float(data['intensity'])

        return btHandle.HSI(h, s, i)

    else:
        logger.warning("Incorrect parameters in data: %s", str(data))

def rgb(btHandle, data):
    if 'red' in data \
        and 'green' in data \
        and 'blue' in data:
        r = int(data['red'])
        g = int(data['green'])
        b = int(data['blue'])

        return btHandle.RGB(r, g, b)

    else:
        logger.warning("Incorrect parameters in data: %s", str(data))

def pulse(btHandle, data):
    if 'freq_hz' in data:
        freq_hz = float(data['freq_hz'])
        return btHandle.pulse(freq_hz)
    else:
        logger.warning("Incorrect parameters in data: %s", str(data))

def blink(btHandle, data):
    if 'freq_hz' in data:
        freq_hz = float(data['freq_hz'])
        return btHandle.blink(freq_hz)
    else:
        logger.warning("Incorrect parameters in data: %s", str(data))

def cycle(btHandle, data):
    if 'period_min' in data \
        and 'saturation' in data \
        and 'intensity' in data:
        period_min = data['period_min']
        saturation = data['saturation']
        intensity = data['intensity']

        return btHandle.cycle(period_min, saturation, intensity)
    else:
        logger.warning("Incorrect parameters in data: %s", str(data))

FUNDICT = {
    'hsi' : hsi,
    'rgb' : rgb,
    'pulse' : pulse,
    'blink' : blink,
    'cycle' : cycle
}

btDevices = dict()

@socketio.on('nanio-event')
def handle_nanio_event(data):
    # var data = {
    #     'module':'couch',
    #     'command':'hsi',
    #     'data': {
    #       'hue':114,
    #       'saturation':1,
    #       'intensity':1
    #     }
    logger.info(str(data))

    # data = json.loads(data)

    if 'module' in data:
        # Specific module
        FUNDICT[data['command']](btDevices[data['module']], data['data'])
    else:
        for key, device in btDevices.items():
            FUNDICT[data['command']](device, data['data'])

@socketio.on('connect')
def connect():
    logger.info('A client connected')
    send('welcome')

class BTThread(threading.Thread):
    btDevices = None
    def __init__(self, _btDevices):
        threading.Thread.__init__(self)
        self.btDevices = _btDevices

    def run(self):
        while True:
            if len(self.btDevices) > 0:
                for key, device in self.btDevices.items():
                    device.do()
                    time.sleep(0.1)

if __name__ == '__main__':
    btDevices['couch'] = BluetoothHandle("98:D3:32:10:A9:7F", 1)
    btDevices['tv'] = BluetoothHandle("98:D3:32:10:AB:7E", 1)

    for key, device in btDevices.items():
        device.connect()

    myBtThread = BTThread(btDevices)

    myBtThread.start()

    socketio.run(app=app, host='0.0.0.0', port=5001)
