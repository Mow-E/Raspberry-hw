# This one is with RFCOMM which will not be used.

""" 
from bluetooth import *
import os

class BluetoothPI:
    def __init__(self):
        
        serverSocket = None

        clientSocket = None
        clientInfo = None

        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    '''
        '''
    def setup(self):

        '''Sudo hciconfig hci0 piscan enables the bluetooth adapter so that it is discoverable for others devices
           sdptool add SP is a tool in blueZ that establishes a Serial port profile SPP service on the device.
           This allows data communication over Bluetooth'''
        
        os.system("sudo hciconfig hci0 piscan")
        os.system("sdptool add SP")

    

        '''These lines of code create a Bluetooth server socket using the RFCOMM protocol,
           bind it to an available port and any IP address, and listen for incoming connections
           where maximum one device at a time can be connected.'''
        self.serverSocket = BluetoothSocket( RFCOMM )
        self.serverSocket.bind(("",PORT_ANY))
        self.serverSocket.listen(1)
        
        '''Allows to advertise a Bluetooth service from this device.'''
        advertise_service( self.serverSocket, "Raspberry PI",
                   service_id = self.uuid,
                   service_classes = [ self.uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
        
        
        print("Waiting for connection on RFCOMM channel %d" %self.serverSocket.getsockname()[1])

        self.clientSocket, self.clientInfo = self.serverSocket.accept()
        print("Accepted connection from ", self.clientInfo)
        
    def retrieveMessage(self):
        ## when recieving messag i first have to decode it before trying to send it through uart.

        '''Recieves a message from device that is connected. If the an error happends
           the client will be disconnected and the the setup will be runned again.'''
        try:
            message = self.clientSocket.recv(1024)
            print("Recieved %s" % message)
            self.clientSocket.close()
            self.serverSocket.close()
            return message
        except IOError:
            print("Disconnected")
            self.clientSocket.close()
            self.socketServer.close()

    def sendMessage(self, message):
        # This one is not neccesary yet that's why it's not implemented.
        b = 1 

 """