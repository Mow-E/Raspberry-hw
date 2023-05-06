 #use serial module
import serial
import time

class SerialUart:
    def __init__(self) -> None:
            self.serialUa = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=9600,
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
        messageFromArduino = self.serialUa.readline().decode()
        self.serialUa.flush()
        return messageFromArduino

""" ser = SerialUart()
ser.setup() """

""" while True:
    message = input("Enter some letter: ")
    ser.write(message.encode())
    time.sleep(1)
    print("Sent: ", message)
    response = ser.readline().decode()
    ser.flush()
    print("Received: ", response) """
    
    
    