import json

from stomp_ws.client import Client
# import logging


def print_frame(frame):
    print(json.loads(frame.body))


if __name__ == '__main__':
    # LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    # logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    # open transport
    client = Client("ws://127.0.0.1:8080/websocket")

    # connect to the endpoint
    client.connect( # Think about the token
        #     username="user",
        #     password="pass",
        timeout=0)

    client.subscribe("/mower/e193c17a-9c4e-4e3b-b2bc-f7a8a31a42b0/queue/coordinate", callback=print_frame)

    while True:
        pass

    # subscribe channel

    client.disconnect()
