 #use serial module
import serial
import time

class SerialUart:
    def __init__(self) -> None:
            self.serialUa = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=115200,
                timeout  = 0.1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
                )
    def setup(self):
        # try to open port, if possible print message
        if self.serialUa.isOpen(): 
            print("port is opened!")
        else:
            print ("port is closed()")
            self.serialUa.open()
            self.serialUa.close()
            self.serialUa.open()
            print ("port was already open, was closed and opened again!")
    
    # Sends message to Arduino
    def sendSerial(self, asciiByteMessage):
        self.serialUa.write(asciiByteMessage)
    
    # Returns message from Arduino
    def retrieveSerial(self):
        if self.serialUa.in_waiting > 0:
            messageFromArduino = self.serialUa.readline().decode()
            self.serialUa.flush()
            return messageFromArduino
        """ while True:
            if self.serialUa.in_waiting > 0:
                messageFromArduino = self.serialUa.readline().decode()
                self.serialUa.flush()
                return messageFromArduino """
                


    
    
    