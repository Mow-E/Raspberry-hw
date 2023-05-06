from bluetoothLowEnergy import *
from raspberryPiCameraV2 import *
from serial1 import *
from mobileDevice import *
import sys


class MowE:
    #mowerID = "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0"
    #mowerID = "44"
    #autenticationCheck = False 
    

    def __init__(self) -> None:
        self.ble = bluetoothLoPo()
        #self.serial = SerialUart()
        self.camera = RasberryPiCameraV2()
    
    def setup(self):
        self.ble.start()
        self.ble.mobile.on('dataReceived', self.retrieveFromApp)
        #self.serial.setup()
    
    def retrieveFromApp(self, data, *args):
        ''' First handle the message '''    
        if args:
            print(f"Extra arguments: {args}")
            for index, arg in enumerate(args):
                data += arg
            print(data)
        else:
            print(data)

        """ if not self.autenticationCheck:
            if data == self.mowerID:
                print("Autentication confirmed")
                self.autenticationCheck = True
            else:
                print("Autentication failed")
                self.ble.disconnect() """
        
        """ message = data.encode('ascii')
            self.serial.sendSerial(message)
            """
    
    def retrieveFromArduino(self):
        pass
        
test = MowE()
test.setup()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    test.ble.stopAdvertising()
    test.ble.disconnect()
    sys.exit(0)