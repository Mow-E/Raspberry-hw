from pybleno import *
from mobileDevice import mobile
import time
import sys

class bluetoothLoPo:
    def __init__(self) -> None:
        # Create a bluetooth instance of Bleno()
        self.bleno = Bleno()
        
    # This creates a callback function that will be called when the state of the instance is changed.
    def setup(self):
        self.bleno.on("stateChange", self.onstateChange)
        self.bleno.on("advertisingStart", self.onAdvertisingStart)
        self.bleno.on("accept", self.onAccept)
        self.bleno.on("disconnect", self.onDisconnect)

    def onstateChange(self, state):
        print(f"on -> stateChange: {state}")

        if state == "poweredOn":
            self.bleno.startAdvertising("Rasberry pi bleno", ["ec00"])
        else:
            self.bleno.stopAdvertising()

    def onAdvertisingStart(self,error):
        if not error:
            print("Advertising started successfully.")
            self.bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec00',
                    'characteristics':[
                        mobile('ec0F')
                    ]
                })
            ])
        else:
            print(f"Advertising failed to start. Error: {error}")

    def onAccept(self, clientAddress):
        print(f"Device connected: {clientAddress}")

    def onDisconnect(self, clientAddress):
        print(f"Device disconnected: {clientAddress}")
    
    def start(self):
        self.setup()
        self.bleno.start()

    def stopAdvertising(self):
        self.bleno.stopAdvertising()
    
    def disconnect(self):
        self.bleno.disconnect()
    def end(self):
        self.bleno.end()

ble = bluetoothLoPo()
ble.start()



try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ble.stopAdvertising()
    ble.disconnect()
    sys.exit(0)