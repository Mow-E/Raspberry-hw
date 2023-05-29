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
    # The mowerID will be used as a password for when the connected device connects. 
    mowerID = "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0"
    autenticationCheck = False

    # These will contain the messages that are being sent from the application connected and the Robot.
    messageFromBluetooth = ""
    messageFromRobot = ""
    
    autonomousDrive = False
    startMoving = False
    manualDrive = False

    # Keeps the timer on when to send coordinates to the server
    websocketTimer = 0
    
    # Will store the values for needed for Wheel-odometry
    previousEncoderLeft = 0
    previousEncoderRight = 0
    thetaChanged = 0
    theta = 0
    xCoordinates = 0
    yCoordinates = 0
   
    
    def __init__(self) -> None:
        # Creates instances of the different classes
        self.ble = bluetoothLoPo()
        self.serial = SerialUart()
        self.camera = RasberryPiCameraV2()
        self.server = Server()
        #self.SLAM = SLAMRPi()

    def setup(self):
        # calls the start and setup functions in each class
        self.ble.start()
        self.ble.mobile.on('dataReceived', self.retrieveFromApp)
        self.ble.emitter.on('disconnectDevice', self.deviceDisconnect)
        self.ble.emitter.on('acceptedClient', self.acceptDevice)
        self.server.setup()
        self.serial.setup()

    # Dead reckoning
    def calculate(self, encoderRight, encoderLeft):
        
        distanceLeft = 2 * math.pi * 2 * (encoderLeft - self.previousEncoderLeft) / 360.0
        distanceRight = 2 * math.pi * 2 * (encoderRight - self.previousEncoderRight) / 360.0

        self.previousEncoderLeft = encoderLeft 
        self.previousEncoderRight = encoderRight

        d = (distanceLeft + distanceRight) / 2.0
        self.thetaChanged = (distanceRight - distanceLeft) / 15

        self.xCoordinates += round(d * math.cos(self.theta + self.thetaChanged / 2.0), 4)
        self.yCoordinates += round(d * math.sin(self.theta + self.thetaChanged / 2.0), 4)
        self.theta += self.thetaChanged

        print("self.y: %d and self.x: %d ", self.yCoordinates, self.xCoordinates)




    # Recive messages from the appication connected
    def retrieveFromApp(self, data, *args):
        # First handle the message    
        if args:
            print(f"Extra arguments: {args}")
            for index, arg in enumerate(args):
                data += arg
            print(data)
        else:
            print(data)
        
        # Checks that the data sent first time from the application is the right mowerID 
        if not self.autenticationCheck:
            self.checkAutenticaiton(data)
        # if passed the autentication the next messages will enter this else statement
        else:
            # Assigns the data from application into the member variable self.messageFromBluetooth
            self.messageFromBluetooth = data
            
            # assigns the bools into the right values and wait for an "GO" from the application 
            if data == 'A':
                self.messageFromBluetooth = ""
                self.serial.notBlockingManuall = False
                self.autonomousDrive = True
                self.manualDrive = False
                self.startMoving = False

            # Starts the mower, and send to the backend the x and y coordinates and that it have started
            elif data == 'G':
                self.startMoving = True
                self.autonomousDrive = True
                self.serial.notBlockingAutonomous = True
                self.server.sendMessageToServer(self.xCoordinates,self.yCoordinates,0)
                if self.autonomousDrive:
                    self.serial.sendSerial('A'.encode("ASCII"))

            # Sets it into manual mode
            elif data == 'M':
                self.websocketTimer = time.time()
                self.serial.notBlockingAutonomous = False
                self.serial.notBlockingManuall = True
                self.autonomousDrive = False
                self.manualDrive = True
                self.startMoving = False
                self.serial.sendSerial('M'.encode("ASCII"))
            
            # Stops the autonomous mode
            elif data == 'O':
                self.serial.sendSerial('M'.encode('ascii'))
                self.serial.sendSerial('S'.encode('ascii'))
                self.server.sendMessageToServer(self.xCoordinates,self.yCoordinates,2)
                self.serial.notBlockingAutonomous = False
                self.startMoving = False
                self.autonomousDrive = False
                #self.manualDrive = True

    # Retrieves the message from the mower.
    def retrieveFromArduino(self):
        self.messageFromRobot = self.serial.retrieveSerial()

    # Checks the autentication from the robot, if passed the device will be able to control the robot otherwise disconnect the device
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

    #Disconnect the device
    def deviceDisconnect(self):
        self.autenticationCheck = False
        self.autonomousDrive = False
        self.manualDrive = False
        self.startMoving = False

        self.serial.sendSerial('M'.encode("ASCII"))
        self.serial.sendSerial('S'.encode("ASCII"))
        self.messageFromBluetooth = ""

        print("disconnect")
    
    # Sending the values to the dead reckoning algorithm  
    def sendToServerTimer(self, encoderX, encoderY):
        self.calculate(int(encoderX), -1*int(encoderY))


    def autonomousMode(self):
        print("Autonomoues mode")

        # Retrieves message from the robot
        self.retrieveFromArduino()
        print("Message from arduino: ",self.messageFromRobot)
        

        # Error
        try:
            if self.messageFromRobot[0] == 'E':
                print("Error")
                try:
                    self.sendToServerTimer(self.messageFromRobot[1],self.messageFromRobot[2])
                    self.server.sendMessageToServer(self.xCoordinates,self.yCoordinates,3)
                    self.messageFromRobot = ""
                except:
                    print("Didn work")
            # Work
            elif self.messageFromRobot[0] == 'W':
                print("Work")
                try:
                    print("Got an W")
                    #self.retrieveFromArduino()
                    self.sendToServerTimer(self.messageFromRobot[1],self.messageFromRobot[2])
                    self.server.sendMessageToServer(self.xCoordinates,self.yCoordinates,1)
                    self.messageFromRobot = ""
                except:
                    print("Didn work")

            # Border
            elif self.messageFromRobot[0] == 'P':
                print("Border")
                try:
                    print("Border")
                    print
                    self.sendToServerTimer(self.messageFromRobot[1],self.messageFromRobot[2])
                    self.server.sendMessageToServer(self.xCoordinates,self.yCoordinates,5)
                    self.messageFromRobot = ""
                except:
                    print("Didn work")

                # Colision
            elif self.messageFromRobot[0] == 'C':
                print("Collision")
                try:
                    self.sendToServerTimer(self.messageFromRobot[1],self.messageFromRobot[2])
                    self.camera.takePicture()
                    self.server.sendMessagePictureToServer(self.xCoordinates,self.yCoordinates,4)
                    self.websocketTimer = time.time()
                    self.messageFromRobot = 'W'
                except:
                    print("Didn work")
        except:
            print("autonomous Didn't work")    

    def start(self):
        while True:
            if self.messageFromBluetooth == "":
               pass 
            else:
                #print("messageFromBluetooth sent to robot: %s ", self.messageFromBluetooth)
                if self.autonomousDrive & self.startMoving:
                    self.autonomousMode()
                    pass
                elif self.manualDrive:
                    #print("Manual")
                    if (time.time() - self.websocketTimer) > 1:
                        print("inside time")
                        try:
                            self.websocketTimer = time.time()
                            self.retrieveFromArduino()
                            self.sendToServerTimer(self.messageFromRobot[1], self.messageFromRobot[2])
                            self.server.sendMessageToServer(self.xCoordinates,self.yCoordinates,1)
                        except:
                            print("didnt work")
                    self.serial.sendSerial(self.messageFromBluetooth.encode("ASCII"))
            
test = MowE()
test.setup()

try:
    test.start()
except KeyboardInterrupt:
    test.serial.serialUa.flush()
    test.serial.sendSerial('M'.encode('ascii'))
    test.serial.sendSerial('S'.encode('ascii'))
    test.serial.serialUa.close()
    test.ble.stopAdvertising()
    test.ble.disconnect()
    test.camera.camera.close()
    sys.exit(0)



