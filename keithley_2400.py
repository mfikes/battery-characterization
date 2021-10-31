import serial
import sys
import time
from enum import Enum

class Keithley_2400():
    addr = None
    gpib = None
    verbose = False

    def __init__(self, gpib, addr=26, verbose=False):
        self.gpib = gpib
        self.addr = addr
        self.verbose = verbose
        self.__command("*rst")
        if (verbose):
            print(self.__query("*idn?"))

    def __command(self, cmd):
        self.gpib.command(self.addr, cmd)

    def __query(self, cmd):
        return self.gpib.query(self.addr, cmd)
    
    def read_voltage(self):
        s = self.__query(":read?")
        vals = s.split(",")
        voltage = float(vals[0])
        return voltage

    def set_off_state_high_impedance(self):
        self.__command(":output:smode himp")

    def set_source_current(self, amps):
        self.__command(":source:current " + str(amps))

    def output_on(self):
        self.__command(":output:state on")

    def output_off(self):
        self.__command(":output:state off")

    def source_current(self):
        self.__command(":system:key 19")

    def measure_voltage(self):
        self.__command(":system:key 15")
        
    def __del__(self):
        self.output_off()
