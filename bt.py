#!/usr/bin/python3

from BluetoothHandle import BluetoothHandle
import time

def main():
    BT1 = BluetoothHandle("98:D3:32:10:AB:7E", 1)
    # BT2 = BluetoothHandle("98:D3:32:10:A9:7F", 1)

    while True:
        BT1.do()
        # BT2.do()


if __name__ == "__main__":
    main()
