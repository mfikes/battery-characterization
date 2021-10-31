import serial
import sys
import time
from enum import Enum

class OutputState(Enum):
    OFF = "off"
    ON = "on"
    
class OffState(Enum):
    NORMAL = "normal"
    HIGH_IMPEDANCE = "himp"

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

    def set_off_state(self, off_state):
        self.__command(":output:smode " + off_state.value)

    def set_source_current(self, amps):
        self.__command(":source:current " + str(amps))

    def set_output_state(self, output_state):
        self.__command(":output:state " + output_state.value)

    def source_current(self):
        self.__command(":system:key 19")

    def measure_voltage(self):
        self.__command(":system:key 15")
        
    def __del__(self):
        self.set_output_state(OutputState.OFF)
