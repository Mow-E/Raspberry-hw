from pybleno import *
from mobileDevice import mobile


class bluetoothLoPo:
    def __init__(self) -> None:
        # Create a bluetooth instance of Bleno() and mobileDevice()
        self.bleno = Bleno()
        self.mobile = mobile('ec0F')
        
    # This creates a callback function that will be called when the state of the instance is changed. "" is the instance and self. is the callbacks function
    def setup(self):
        self.bleno.on("stateChange", self.onstateChange)
        self.bleno.on("advertisingStart", self.onAdvertisingStart)
        self.bleno.on("accept", self.onAccept)
        self.bleno.on("disconnect", self.onDisconnect)

    # This will check if the BLE radio is powered on, if so it will start to to advertise.
    def onstateChange(self, state):
        print(f"on -> stateChange: {state}")

        if state == "poweredOn":
            self.bleno.startAdvertising("Rasberry pi bleno", ["ec00"])
        else:
            self.bleno.stopAdvertising()
            
    # This will be triggered when the advertising is on or off.
    def onAdvertisingStart(self,error):

        # If no error then it sets the service provided by the BLE pheripheral.
        # For example when a app connects to the raspberry pi it can interract with this service.
        if not error:
            print("Advertising started successfully.")
            self.bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec00',
                    'characteristics':[
                        self.mobile
                    ],
                })
            ])
        else:
            print(f"Advertising failed to start. Error: {error}")

    # When a device is connected it will print its adress.
    def onAccept(self, clientAddress):
        print(f"Device connected: {clientAddress}")

    # When a device is disconnected it will print its adress.
    def onDisconnect(self, clientAddress):
        print(f"Device disconnected: {clientAddress}")
    
    # Starts the bluetooth module 
    def start(self):
        self.setup()
        self.bleno.start()

    def stopAdvertising(self):
        self.bleno.stopAdvertising()
    
    def disconnect(self):
        self.bleno.disconnect()

""" test = bluetoothLoPo()
test.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    test.stopAdvertising()
    test.disconnect()
    sys.exit(0) """