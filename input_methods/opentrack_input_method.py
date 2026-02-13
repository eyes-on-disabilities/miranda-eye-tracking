from typing import Optional

from input_methods.clients.opentrack_client import OpentrackClient
from input_methods.input_method import InputMethod
from misc import Vector

import logging


class OpentrackInputMethod(InputMethod):

    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.opentrack = OpentrackClient()
        self.logger.info("initialized")

    def start(self):
        self.opentrack.start()
        self.logger.info("started")

    def stop(self):
        self.opentrack.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        head = self.opentrack.get_last_data()
        next_vector = (head["yaw"],
                       head["pitch"]) if head is not None else None
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
