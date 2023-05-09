import base64
import datetime
import json
import os
import secrets
import time

from stomp_ws.client import Client
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

STATE_START = 0
STATE_WORK = 1
STATE_END = 2
STATE_ERROR = 3
STATE_COLLISION = 4

# define chunk size in bytes
CHUNK_SIZE = 4000


def response(x, y, z, state, extended=""):
    return json.dumps(
        {
            'mowerId': os.getenv('MOWER_ID'),
            'x': x,
            'y': y,
            'z': z,
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
    z = 3

    client.send("/app/coordinate", body=response(x, y, z, STATE_START))

    time.sleep(2)

    for i in range(5):
        time.sleep(1)
        x = x + 1
        y = y + 1
        z = z + 1
        if i != 4:
            # send msg to channel
            client.send("/app/coordinate", body=response(x, y, z, STATE_WORK))
        else:
            # extended = str(base64.encode(secrets.token_bytes(8)))
            id = int.from_bytes(secrets.token_bytes(4), "big")
            # extended = str(int.from_bytes(id, "big"))

            client.send("/app/coordinate", body=response(x, y, z, STATE_COLLISION, str(id)))

            time.sleep(1)
            with open('data/images/test_image_4.jpg', 'rb') as f:
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

    client.send("/app/coordinate", body=response(x, y, z, STATE_END))

    client.disconnect()
