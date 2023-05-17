from bluetoothLowEnergy import *
from raspberryPiCameraV2 import *
from websocket_client import *
from serial1 import *
from mobileDevice import *
import sys


class MowE:
    mowerID = "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0"
    #mowerID = "44"
    autenticationCheck = False
    messageFromBluetooth = ""
    messageFromRobot = ""
    autonomousDrive = False
    startMoving = False
    manualDrive = False  
    
    def __init__(self) -> None:
        # implement: Close bluetooth then turn it on because of issues.

        self.ble = bluetoothLoPo()
        self.serial = SerialUart()
        self.camera = RasberryPiCameraV2()
        self.server = Server()
    
    def setup(self):
        self.ble.start()
        self.ble.mobile.on('dataReceived', self.retrieveFromApp)
        self.ble.emitter.on('disconnectDevice', self.deviceDisconnect)
        self.ble.emitter.on('acceptedClient', self.acceptDevice)
        #self.server.setup()
        self.serial.setup()
    
    def retrieveFromApp(self, data, *args):
        # First handle the message    
        if args:
            print(f"Extra arguments: {args}")
            for index, arg in enumerate(args):
                data += arg
            print(data)
        else:
            print(data)

        if not self.autenticationCheck:
            self.checkAutenticaiton(data)
        
        else:
            self.messageFromBluetooth = data
            if data == 'A':
                self.autonomousDrive = True
                self.manualDrive = False
                self.startMoving = False
            elif data == 'G':
                self.startMoving = True
                if self.autonomousDrive:
                    self.serial.sendSerial('A'.encode("ASCII"))
            elif data == 'M':
                self.autonomousDrive = False
                self.manualDrive = True
                self.startMoving = False
                self.serial.sendSerial('M'.encode("ASCII"))
            elif data == 'O':
                self.serial.sendSerial('M'.encode('ascii'))
                self.serial.sendSerial('S'.encode('ascii'))
                self.startMoving = False

    
    def retrieveFromArduino(self):
        self.messageFromRobot = self.serial.retrieveSerial()

    def checkAutenticaiton(self, data):
        if data == self.mowerID:
            print("Autentication confirmed")
            self.autenticationCheck = True
        else:
            print("Autentication failed")
            self.ble.disconnect()

    def acceptDevice(self):
        pass
        # Kanske andra saker här


    def deviceDisconnect(self):
        self.autenticationCheck = False
        self.autonomousDrive = False
        self.manualDrive = False
        self.startMoving = False

        
        self.serial.sendSerial('M'.encode("ASCII"))
        self.serial.sendSerial('S'.encode("ASCII"))
        self.messageFromBluetooth = ""

        # Alternativt annat här
        self.messageFromRobot = ""
        print("disconnect")
    
    def start(self):
        while True:
            time.sleep(1)
            if self.messageFromBluetooth == "":
               print("empty") 
            else:
                print("messageFromBluetooth sent to robot: %s ", self.messageFromBluetooth)
                if self.autonomousDrive & self.startMoving:
                    print("before retrieveFromArduino")
                    self.retrieveFromArduino()
                    print("Message from arduino: ",self.messageFromRobot)
                    
                    print("Autonomoues mode")
                    # Error
                    if self.messageFromRobot == 'E':
                        print("Got an E")
                        pass
                    # Start
                    elif self.messageFromRobot == 'S':
                        print("Got an S")
                    # Work
                    elif self.messageFromRobot == 'W':
                        print("Got an W")
                    # End
                    elif self.messageFromRobot == 'D':
                        print("Got an D")
                    # Colision
                    elif self.messageFromRobot == 'C':
                        print("Collision")
                        # Take picture, x and y cordinates and then send it to backend after that send back to robot that you are done
                        self.camera.takePicture()
                        #self.server.sendMessagePictureToServer(1,2,3)
                        self.messageFromRobot = 'W'
                elif self.manualDrive:
                    print("Manual")
                    self.serial.sendSerial(self.messageFromBluetooth.encode("ASCII"))
                    
                    # Skickar bara X och Y cordinater här 
        
test = MowE()
test.setup()

try:
    test.start()
except KeyboardInterrupt:
    test.ble.stopAdvertising()
    test.ble.disconnect()
    sys.exit(0)