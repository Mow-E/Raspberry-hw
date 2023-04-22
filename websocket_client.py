import datetime
import json
import os
import time

from stomp_ws.client import Client
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

STATE_START = 0
STATE_WORK = 1
STATE_END = 2
STATE_ERROR = 3
STATE_COLLISION = 4


def response(x, y, state):
    return json.dumps(
        {
            'mowerId': "e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0",
            'x': x,
            'y': y,
            'time': int(datetime.datetime.now().timestamp()),
            'state': state
        }
    )


if __name__ == '__main__':

    # open transport
    client = Client("ws://127.0.0.1:8080/websocket")

    # connect to the endpoint
    client.connect(headers={"x-auth-token": os.getenv("TOKEN")}, timeout=0)

    x = 1
    y = 2

    client.send("/app/coordinate", body=response(x, y, STATE_START))

    time.sleep(2)

    for i in range(5):
        time.sleep(1)
        x = x + 1
        y = y + 1
        # send msg to channel
        client.send("/app/coordinate", body=response(x, y, STATE_WORK))

    time.sleep(1)

    client.send("/app/coordinate", body=response(x, y, STATE_END))

    client.disconnect()
