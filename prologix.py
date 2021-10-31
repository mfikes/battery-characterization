import serial
import sys
import time

class Prologix():
    ser = None
    curr_addr = None
    verbose = False

    def __init__(self,port,verbose=False):
        self.verbose = verbose
        self.ser = serial.Serial(port, timeout=1)
        self.reset()
        self.write("++mode 1")
        self.write("++auto 0")
        self.write("++eos 3")
        self.write("++eoi 1")

    def reset(self):
        self.write("++rst")
        # The Prologix User Manual indicates rst takes about 5 seconds
        # We wait for 6 seconds and ensure reset is complete by reading
        # the Prologix device version
        time.sleep(6)
        self.write("++ver")
        ver = self.read()
        if len(ver) == 0:
            raise Exception("Couldn't read the Prologix device version")
        
    def write(self,cmd):
        if self.verbose:
            print("prologix >>> " + cmd)
        self.ser.write(bytes(cmd + "\n", "utf-8"))

    def read(self):
        s = (self.ser.readline().decode()).strip()
        if self.verbose:
            print("prologix <<< " + s)
        return s
        
    def command(self,addr,cmd,delay=0.0):
        if (addr != self.curr_addr):
            self.write("++addr " + str(addr))
            self.curr_addr = addr
        self.write(cmd)
        if (delay != 0.0):
            time.sleep(delay)

    def query(self,addr,cmd,delay=0.1):
        self.command(addr,cmd,delay)
        self.write("++read eoi")
        return self.read()

    def __del__(self):
        self.reset()
        self.ser.close()
