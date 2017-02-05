#!/usr/bin/python3

from api import app
from naniologger import logger
import bthandler
import bluetooth

def main():
    #app.run(host='0.0.0.0', port=5000, debug=True)
    # SERIALPORT_SERVICE_UUID = "00001101-0000-1000-8000-00805f9b34fb"
    # SERIALPORT_SERVICE_UUID = "1101"
    ADDRESS = "98:D3:32:10:AB:7E"
    # bthandler.search_nearby_devices()
    bthandler.connect_to_service(ADDRESS, bluetooth.SERIAL_PORT_CLASS)
    # bthandler.connect_to_service(ADDRESS, SERIALPORT_SERVICE_UUID)

if __name__ == "__main__":
    main()
