import base64
import datetime
import json
import os
import secrets
import time

from stomp_ws.client import Client
from dotenv import load_dotenv

load_dotenv()  

STATE_START = 0
STATE_WORK = 1
STATE_END = 2
STATE_ERROR = 3
STATE_COLLISION = 4
STATE_BORDER = 5

# define chunk size in bytes
CHUNK_SIZE = 4000

class Server:
    def __init__(self):
        load_dotenv() # take environment variables from .env. 
    
    def setup(self):
        self.client = Client(f"ws://{os.getenv('HOST')}:{os.getenv('PORT')}/websocket")

        # connect to the endpoint
        self.client.connect(headers={"x-auth-token": os.getenv("TOKEN")}, timeout=0)

        

    def response(self, x, y, state, extended=""):
        return json.dumps(
            {
                'mowerId': "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0",
                'x': x,
                'y': y,
                'time': int(datetime.datetime.now().timestamp()),
                'state': state,
                'extra': extended
            }
        )

    def sendMessageToServer(self, x, y, state):
        self.client.send("/app/coordinate",None,body=self.response(x, y, state))
        print("Only message send to server")

    def sendMessagePictureToServer(self, x, y, state):
        # extended = str(base64.encode(secrets.token_bytes(8)))
        id = int.from_bytes(secrets.token_bytes(4), "big")
        # extended = str(int.from_bytes(id, "big"))

        self.client.send("/app/coordinate", None ,body=self.response(x, y, state, str(id)))

        time.sleep(1)
        with open('/home/admin/Documents/Embedded/RaspberryPiPhotos/test.jpg', 'rb') as f:
            image_data = f.read()
            # data += image_data

            # get size of image data in bytes
            data_size = len(image_data)

            # determine number of chunks needed
            num_chunks = (data_size + CHUNK_SIZE - 1) // CHUNK_SIZE

            # create chunks from image data
            for i in range(num_chunks):
                chunk_data = image_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]

                self.client.send("/app/images/add",None,body=json.dumps(
                    {
                        'id': id,
                        'chunkAmount': num_chunks,
                        'chunkOffset': i,
                        'data': str(base64.b64encode(chunk_data).decode("utf-8"))
                    }))
                
""" def response(x, y, state, extended=""):
        return json.dumps(
            {
                'mowerId': "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0",
                'x': x,
                'y': y,
                'time': int(datetime.datetime.now().timestamp()),
                'state': state,
                'extra': extended
            }
        )



if __name__ == '__main__':

    # open transport
    client = Client(f"ws://{os.getenv('HOST')}:{os.getenv('PORT')}/websocket")

    # connect to the endpoint
    client.connect(headers={"x-auth-token": os.getenv("TOKEN")}, timeout=0)

    x = 1
    y = 2

    client.send("/app/coordinate", body=response(x=x, y=y, state=STATE_START))

    time.sleep(2)

    for i in range(5):
        time.sleep(1)
        x = x + 1
        y = y + 1
        if i != 4:
            # send msg to channel
            client.send("/app/coordinate", body=response(x, y, STATE_WORK))
        else:
            # extended = str(base64.encode(secrets.token_bytes(8)))
            id = int.from_bytes(secrets.token_bytes(4), "big")
            # extended = str(int.from_bytes(id, "big"))

            client.send("/app/coordinate", body=response(x, y, STATE_COLLISION, str(id)))

            time.sleep(1)
            with open('/home/admin/Documents/Embedded/RaspberryPiPhotos/test.jpg', 'rb') as f:
                image_data = f.read()
                # data += image_data

                # get size of image data in bytes
                data_size = len(image_data)

                # determine number of chunks needed
                num_chunks = (data_size + CHUNK_SIZE - 1) // CHUNK_SIZE

                # create chunks from image data
                for i in range(num_chunks):
                    chunk_data = image_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]

                    client.send("/app/images/add", body=json.dumps(
                        {
                            'id': id,
                            'chunkAmount': num_chunks,
                            'chunkOffset': i,
                            'data': str(base64.b64encode(chunk_data).decode("utf-8"))
                        }))

    time.sleep(1)

    client.send("/app/coordinate", body=response(x, y, STATE_END))

    client.disconnect() """
