import json
import os

from stomp_ws.client import Client
from dotenv import load_dotenv
# import logging

load_dotenv()  # take environment variables from .env.

def print_frame(frame):
    print(json.loads(frame.body))



if __name__ == '__main__':
    # LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    # logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    # open transport
    # client = Client(f"ws://{os.getenv('HOST')}:{os.getenv('PORT')}/websocket")
    client = Client(f"ws://{os.getenv('HOST')}/websocket")

    # connect to the endpoint
    client.connect(headers={"x-auth-token": os.getenv("TOKEN")}, timeout=0)

    client.subscribe(f"/mower/{os.getenv('MOWER_ID')}/queue/coordinate", callback=print_frame)

    while True:
        pass

    # subscribe channel

    client.disconnect()
