#!/usr/bin/python3

from naniologger import logger
import bluetooth
import time
import datetime
import select
from threading import Lock

RGB_IDENTIFIER = 99  # c
HSI_IDENTIFIER = 104  # h
INTENSITY_IDENTIFIER = 105  # i
PULSE_IDENTIFIER = 112  # p
BLINK_IDENTIFIER = 98  # b
CYCLE_IDENTIFIER = 72  # H

HEARTBEAT_TIMEOUT = 10 # seconds


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class BluetoothHandle:
    addr = ""
    port = 0
    btSocket = None
    lastHeartbeat = None
    connected = False
    lock = Lock()

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def connect(self):
        if not self.connected:
            try:
                self.btSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.btSocket.setblocking(True)
                logger.info("Connecting to %s port %d", self.addr, self.port)
                self.btSocket.settimeout(None)
                self.btSocket.connect((self.addr, self.port))
                logger.info("Connected to %s port %d", self.addr, self.port)
                self.btSocket.settimeout(0.1)
                self.connected = True
                return True
            except IOError as e:
                logger.error(e)
                if '113' in e.args[0]:
                    logger.error("herple")
                    # No route to host
                    # wat do?
                return False

    def disconnect(self):
        logger.info("Disconnecting from %s", self.addr)
        self.btSocket.close()
        self.btSocket = None
        self.connected = False

    def HSI(self, hue, sat, intensity):
        h1 = int(clamp(hue / 10, 0, 36))
        h2 = int(clamp((hue - h1 * 10) * 10, 0, 99))
        sat = int(clamp(sat * 100, 0, 100))
        intensity = int(clamp(intensity * 100, 0, 100))
        logger.info("%s - Sending HSI packet {h.%d.%d.%d.%d}", self.addr, h1, h2, sat, intensity)
        self.send_data(HSI_IDENTIFIER, h1, h2, sat, intensity)
        self.recv_data()

    def RGB(self, red, green, blue):
        red = int(clamp(red, 0, 255))
        green = int(clamp(green, 0, 255))
        blue = int(clamp(blue, 0, 255))
        logger.info("Sending RGB packet {c.%d.%d.%d.--}", red, green, blue)
        self.send_data(RGB_IDENTIFIER, red, green, blue)
        self.recv_data()

    def intensity(self, intensity):
        # intensity should be between 0 and 1
        i1 = int(clamp(intensity * 100, 0, 100))
        logger.info("Sending intensity packet {i.%d.--.--.--}", intensity)
        self.send_data(INTENSITY_IDENTIFIER, i1)
        self.recv_data()

    def pulse(self, pulse_freq_hz):
        pulse_period_ms = int(1000 / pulse_freq_hz)

        # Clamp above epileptic frequency
        if pulse_period_ms < 125:
            pulse_period_ms = 125

        p1 = int(pulse_period_ms / 100)
        p2 = int((pulse_period_ms / 100 - int(pulse_period_ms / 100)) * 100)
        logger.info("Sending pulse packet {p.%d.%d.--.--}")
        self.send_data(PULSE_IDENTIFIER, p1, p2)
        self.recv_data()

    def blink(self, blink_freq_hz):
        blink_period_ms = int(1000 / blink_freq_hz)

        # Clamp above epileptic frequency
        if blink_period_ms < 125:
            blink_period_ms = 125

        b1 = int(blink_period_ms / 100)
        b2 = int((blink_period_ms / 100 - int(blink_period_ms / 100)) * 100)
        logger.info("Sending blink packet {b.%d.%d.--.--}")
        self.send_data(BLINK_IDENTIFIER, b1, b2)
        self.recv_data()

    def cycle(self, period_mins, saturation, intensity):
        if period_mins < 1:
            period_mins = 1  # clamp to above 1 minute

        p1 = int(period_mins)
        s1 = int(clamp(saturation * 100, 0, 100))
        i1 = int(clamp(intensity * 100, 0, 100))

        logger.info("Sending cycle packet {H.%d.%d.%d.--}", p1, s1, i1)
        self.send_data(CYCLE_IDENTIFIER, p1, s1, i1)
        self.recv_data()

    def send_data(self, *args):
        self.lock.acquire()
        message = bytearray()
        message.append(123)
        for arg in args:
            message.append(arg)
        # Pad with zeroes if needed
        while len(message) < 6:
            message.append(0)
        message.append(125)
        if len(message) == 7:
            try:
                self.btSocket.send(bytes(message))
            except IOError as e:
                logger.error(e)
        else:
            logger.warning(
                "Ignored packet with incorrect length %d (should be 7)", len(message))

        self.lock.release()
        # logger.info("Lock released")

    def recv_data(self):
        self.lock.acquire()
        input = [self.btSocket]
        output = [self.btSocket]
        msgbuffer = bytes()
        while True:
            # logger.info("Waiting for input on %s...", self.addr)
            inputready, outputready, exceptready = select.select(input, output, [])

            # logger.info(outputready)
            try:
                data = self.btSocket.recv(1024)
                msgbuffer += data
            except IOError as e:
                if 'timed out' not in e.args[0]:
                    logger.error(e)
                break
        self.lock.release()
        return msgbuffer

    def check_heartbeat(self):
        hb = self.recv_data()
        if len(hb) == 5:
            # logger.info("Heartbeat received from %s", self.addr)
            self.lastHeartbeat = datetime.datetime.now()
            return True
        else:
            if self.lastHeartbeat != None:
                delta = datetime.datetime.now() - self.lastHeartbeat
                if delta.seconds > HEARTBEAT_TIMEOUT:
                    # we have disconnected!
                    return False
                else:
                    return True
            else:
                logger.info("Heartbeat not established yet")
                return True

    def do(self):
        if self.connected:
            if not self.check_heartbeat():
                # do the reconnection dances
                logger.warn("Heartbeat not received within %ds", HEARTBEAT_TIMEOUT)
                self.disconnect()
                logger.info("Attempting reconnection...")
                self.connect()
        else:
            self.connect()
