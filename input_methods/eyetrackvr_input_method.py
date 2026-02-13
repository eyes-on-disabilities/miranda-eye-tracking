from typing import Optional

from input_methods.input_method import InputMethod
from misc import Vector
from input_methods.clients.eyetrackvr_client import EyeTrackVRClient

import logging


class EyeTrackVRInputMethod(InputMethod):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.eyetrackvr = EyeTrackVRClient()
        self.logger.info("initialized")

    def start(self):
        self.eyetrackvr.start()
        self.logger.info("started")

    def stop(self):
        self.eyetrackvr.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        next_vector = self.eyetrackvr.get_last_data()
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
