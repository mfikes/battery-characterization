import serial
import sys
import time

class Prologix():
    ser = None

    def __init__(self,port):
        self.ser = serial.Serial(port, timeout=1)
        self.write("++rst")
        self.write("++mode 1")
        self.write("++auto 0")
        self.write("++eos 3")
        self.write("++eoi 1")

    def write(self,cmd):
        self.ser.write(bytes(cmd + "\n", "utf-8"))

    def command(self,addr,cmd,delay=0.0):
        self.write("++addr " + str(addr))
        self.write(cmd)
        if (delay != 0.0):
            time.sleep(delay)

    def query(self,addr,cmd,delay=0.1):
        self.command(addr,cmd,delay)
        self.write("++read eoi")
        return (self.ser.readline().decode()).strip()

    def __del__(self):
        self.write("++rst")
        self.ser.close()
