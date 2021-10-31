import serial
import sys
import time

class Keithley_2400():
    addr = None
    gpib = None
    verbose = False

    def __init__(self,gpib,addr,verbose=False):
        self.gpib = gpib
        self.addr = addr
        self.verbose = verbose

    def __del__(self):
        self.reset()
        self.ser.close()
