from bluetoothLowEnergy import *
from raspberryPiCameraV2 import *
from websocket_client import *
from serial1 import *
from mobileDevice import *
import sys
import time
from SLAMRPi import *
import math

x = 0
y = 0

class MowE:
    mowerID = "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0"
    #mowerID = "44"
    autenticationCheck = False
    messageFromBluetooth = ""
    messageFromRobot = ""
    autonomousDrive = False
    startMoving = False
    manualDrive = False

    websocketTimer = 0
    websocketSend = False
    test = False
    previousEncoderLeft = 0
    previousEncoderRight = 0

    thetaChanged = 0
    theta = 0

    x = 0
    y = 0
   
    
    def __init__(self) -> None:
        # implement: Close bluetooth then turn it on because of issues. 
        self.ble = bluetoothLoPo()
        self.serial = SerialUart()
        self.camera = RasberryPiCameraV2()
        self.server = Server()
        #self.SLAM = SLAMRPi()

    def setup(self):
        self.ble.start()
        self.ble.mobile.on('dataReceived', self.retrieveFromApp)
        self.ble.emitter.on('disconnectDevice', self.deviceDisconnect)
        self.ble.emitter.on('acceptedClient', self.acceptDevice)
        self.server.setup()
        self.serial.setup()   
    
    def calculate(self, encoderRight, encoderLeft):
        
        dLeft = 2 * math.pi * 2 * (encoderLeft - self.previousEncoderLeft) / 360.0
        dRight = 2 * math.pi * 2 * (encoderRight - self.previousEncoderRight) / 360.0

        self.previousEncoderLeft = encoderLeft 
        self.previousEncoderRight = encoderRight

        d = (dLeft + dRight) / 2.0
        self.thetaChanged = (dRight - dLeft) / 15

        self.x += round(d * math.cos(self.theta + self.thetaChanged / 2.0), 4)
        self.y += round(d * math.sin(self.theta + self.thetaChanged / 2.0), 4)
        self.theta += self.thetaChanged

        print("self.y: %d and self.x: %d ", self.y, self.x)





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
                self.messageFromBluetooth = ""
                self.autonomousDrive = True
                self.manualDrive = False
                self.startMoving = False

            elif data == 'G':
                self.startMoving = True
                self.server.sendMessageToServer(self.x,self.y,0)
                if self.autonomousDrive:
                    self.serial.sendSerial('A'.encode("ASCII"))

            elif data == 'M':
                self.websocketTimer = time.time()
                self.autonomousDrive = False
                self.manualDrive = True
                self.startMoving = False
                self.serial.sendSerial('M'.encode("ASCII"))

            elif data == 'O':
                self.serial.sendSerial('M'.encode('ascii'))
                self.serial.sendSerial('S'.encode('ascii'))
                self.server.sendMessageToServer(self.x,self.y,2)
                self.startMoving = False
                self.autonomousDrive = False
                self.manualDrive = True

    
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

        print("disconnect")
    
    def autonomousMode(self):
        print("Autonomoues mode")

        self.retrieveFromArduino()
        print("Message from arduino: ",self.messageFromRobot)
        
        # Error
        if self.messageFromRobot == 'E':
            print("Error")
            try:
                self.sendToServerTimer()
                self.server.sendMessageToServer(x,y,3)
                self.messageFromRobot = ""
            except:
                print("Didn work")
        # Work
        elif self.messageFromRobot == 'W':
            print("Work")
            try:
                print("Got an W")
                self.sendToServerTimer()
                self.server.sendMessageToServer(self.x,self.y,1)
                self.messageFromRobot = ""
            except:
                print("Didn work")

        # Border
        elif self.messageFromRobot == 'P':
            print("Border")
            try:
                print("Border")
                self.sendToServerTimer()
                self.server.sendMessageToServer(self.x,self.y,5)
                self.messageFromRobot = ""
            except:
                print("Didn work")

            # Colision
        elif self.messageFromRobot == 'C':
            print("Collision")
            try:
                self.sendToServerTimer()
                self.camera.takePicture()
                self.server.sendMessagePictureToServer(self.x,self.y,4)
                self.websocketTimer = time.time()
                self.messageFromRobot = 'W'
            except:
                print("Didn work")
        

    def sendToServerTimer(self):
        
        self.serial.serialUa.flush()
        self.serial.sendSerial("X".encode("ASCII"))
        encoderXAndEncoderY = self.serial.serialUa.readline().decode().strip()
        print(encoderXAndEncoderY)
        self.serial.serialUa.flush()


        encoderValues = encoderXAndEncoderY.split(' ')
       
        self.calculate(int(encoderValues[0]), -1*int(encoderValues[1]))
    
    def start(self):
        while True:
            #time.sleep(1)
            if self.messageFromBluetooth == "":
               #print("empty")
               pass 
            else:
                #print("messageFromBluetooth sent to robot: %s ", self.messageFromBluetooth)
                if self.autonomousDrive & self.startMoving:
                    #self.sendToServerTimer()
                    self.autonomousMode()
                elif self.manualDrive:
                    #print("Manual")
                    if (time.time() - self.websocketTimer) > 1:
                        print("inside time")
                        try:
                            self.sendToServerTimer()
                            self.websocketTimer = time.time()
                            self.server.sendMessageToServer(self.x,self.y,1)
                            
                            
                        except:
                            print("didnt work")
                    self.serial.sendSerial(self.messageFromBluetooth.encode("ASCII"))
            
test = MowE()
test.setup()

try:
    test.start()
except KeyboardInterrupt:
    test.ble.stopAdvertising()
    test.ble.disconnect()
    test.camera.camera.close()
    sys.exit(0)