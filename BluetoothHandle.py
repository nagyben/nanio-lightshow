#!/usr/bin/python3

from naniologger import logger
import bluetooth
import time

RGB_IDENTIFIER          = 99  # c
HSI_IDENTIFIER          = 104 # h
INTENSITY_IDENTIFIER    = 105 # i
PULSE_IDENTIFIER        = 112 # p
BLINK_IDENTIFIER        = 98  # b
CYCLE_IDENTIFIER        = 72  # H

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class BluetoothHandle:
    addr = ""
    port = 0
    btSocket = None

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.btSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.btSocket.settimeout(0)

    def connect(self):
        try:
            logger.info("Connecting to %s port %d", self.addr, self.port)
            self.btSocket.connect((self.addr, self.port))
        except IOError as e:
            logger.error(e)
            if '113' in e.args[0]:
                logger.error("herple")
                # No route to host
                # wat do?
                pass


    def HSI(self, hue, sat, intensity):
        h1 = int(clamp(hue / 10, 0, 36))
        h2 = int(clamp(hue - int(hue), 0, 99))
        sat = int(clamp(sat * 100, 0, 100))
        intensity = int(clamp(intensity * 100, 0, 100))
        logger.info("Sending HSI packet {h.%d.%d.%d.%d}", h1, h2, sat, intensity)
        self.send_data(HSI_IDENTIFIER, h1, h2, sat, intensity)

    def RGB(self, red, green, blue):
        red = int(clamp(red, 0, 255))
        green = int(clamp(green, 0, 255))
        blue = int(clamp(blue, 0, 255))
        logger.info("Sending RGB packet {c.%d.%d.%d.--}", red, green, blue)
        self.send_data(RGB_IDENTIFIER, red, green, blue)

    def intensity(self, intensity):
        # intensity should be between 0 and 1
        i1 = int(clamp(intensity * 100, 0, 100))
        logger.info("Sending intensity packet {i.%d.--.--.--}", intensity)
        self.send_data(INTENSITY_IDENTIFIER, i1)

    def pulse(self, pulse_freq_hz):
        pulse_period_ms = int(1000 / pulse_freq_hz)

        # Clamp above epileptic frequency
        if pulse_period_ms < 125:
            pulse_period_ms = 125

        p1 = int(pulse_period_ms / 100)
        p2 = int((pulse_period_ms / 100 - int(pulse_period_ms / 100)) * 100)
        logger.info("Sending pulse packet {p.%d.%d.--.--}")
        self.send_data(PULSE_IDENTIFIER, p1, p2)

    def blink(self, blink_freq_hz):
        blink_period_ms = int(1000 / blink_freq_hz)

        # Clamp above epileptic frequency
        if blink_period_ms < 125:
            blink_period_ms = 125

        b1 = int(blink_period_ms / 100)
        b2 = int((blink_period_ms / 100 - int(blink_period_ms / 100)) * 100)
        logger.info("Sending blink packet {b.%d.%d.--.--}")
        self.send_data(BLINK_IDENTIFIER, b1, b2)

    def cycle(self, period_mins, saturation, intensity):
        if period_mins < 1:
            period_mins = 1 # clamp to above 1 minute

        p1 = int(period_mins)
        s1 = int(clamp(saturation, 0, 100))
        i1 = int(clamp(intensity, 0, 100))

        logger.info("Sending cycle packet {H.%d.%d.%d.--}", p1, s1, i1)
        self.send_data(CYCLE_IDENTIFIER, p1, s1, i1)


    def send_data(self, *args):
        message = bytearray()
        message.append(123)
        for arg in args:
            message.append(arg)

        # Pad with zeroes if needed
        while len(message) < 6:
            message.append(0)

        message.append(125)
        if len(message) == 7:
            logger.info("Sending %s", bytes(message))
            try:
                self.btSocket.send(bytes(message))
                msgbuffer = bytes()
                while True:
                    try:
                        data = self.btSocket.recv(128)
                        msgbuffer += data
                        if len(data) == 0:
                            print("break")
                            # print(str(msgbuffer, "utf-8"))
                            logger.info("Response from module: %s", str(msgbuffer, "utf-8"))
                            break
                    except IOError as e:
                        logger.error(e)
                        # logger.info(data)

            except IOError as e:
                logger.error(e)
                if  '107' in e.args[0]:
                    # Transport endpoint not connected
                    self.connect()

        else:
            logger.warning("Ignored packet with incorrect length %d (should be 7)", len(message))
