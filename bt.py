#!/usr/bin/python3

from BluetoothHandle import BluetoothHandle
import time

def main():
    BT1 = BluetoothHandle("98:D3:32:10:AB:7E", 1)
    BT1.connect()

    while True:
        BT1.HSI(360, 1, 0)
        time.sleep(0.1)
        BT1.HSI(360, 1, 1)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
