from pybleno import Characteristic
from pyee import EventEmitter

''' Charasteristics from pybleno
    This will be the charasteristics of the connected device. It will be able to read, write data.
    recievedData: a bytearray which will store the data from the connected device.
    '''
class mobile(Characteristic, EventEmitter):

    def __init__(self, uuid):
        self.recievedData = bytearray()
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read','write'],
            'value': None
        })

    ''' onReadRequest handles the input from the central device.
        Parameters:
        offset: This is the starting index at which the central device want to write the data, will start at 0.
        callback: This you need to call once you have prepared the data you want to sent to the connected device.
        '''
    def onReadRequest(self, offset, callback):
        data = bytearray('e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0+463208951+Automover 310 Mark II+AM5369841', 'ASCII')
        callback(Characteristic.RESULT_SUCCESS,data[offset:] )
    
    ''' onWriteRequest handles the input from the connected device.
        Parameters:
        data: This is a bytearray and is the data that is being sent from the connected device.
        offset: This is the starting index at which the central device want to write the data, will start at 0.
        withoutResponse: is used to specify wheter the write operation requires a response from the connected 
                         device after the data is written.
        callback: This you need to call after you have proccessed the data. 
        '''
    
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        print("onWriteRequest")
        # Checks if the offset is not zero, which means that it will not start to read from the first position.
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
            
            
            '''else: 
                It will add the data into the bytearray revievedData, after it will check if the added data is a '*' which acts
                like a delimiter. If so it will remove the '*', print it on the console, copy its 
                bytearray into dataToSerialUart and then return it.
            '''
        else:
            self.recievedData.extend(data)
            if b'*' in data:
                self.recievedData.pop()
                if len(self.recievedData):
                    dataToSerialUart = self.recievedData.decode('ASCII')
                    self.recievedData.clear()
                    print(dataToSerialUart)
                    self.emit('dataReceived', dataToSerialUart)
                else:
                    print("Empty")
            callback(Characteristic.RESULT_SUCCESS)
        