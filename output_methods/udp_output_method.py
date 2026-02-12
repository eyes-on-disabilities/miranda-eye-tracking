import json
import socket
from datetime import datetime

from output_methods.output_method import Publisher
from misc import Vector

import logging


class UdpPublisher(Publisher):
    """Pushes the vector as JSON objects over UDP"""

    def __init__(self, root_window, host="127.0.0.1", port=9999):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sock = None
        self.server_address = (host, port)
        self.logger.info("initialized")

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger.info("started")

    def stop(self):
        self.sock.close()
        self.logger.info("stopped")

    def push(self, vector: Vector):
        message = {"x": vector[0], "y": vector[1], "timestamp": str(datetime.now())}
        json_message = json.dumps(message)
        self.sock.sendto(json_message.encode(), self.server_address)
        self.logger.debug(f"pushed vector: {vector}")
