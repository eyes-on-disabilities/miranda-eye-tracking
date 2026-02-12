from typing import Optional

from input_methods.input_method import DataSource
from misc import Vector
from input_methods.clients.eyetrackvr import EyeTrackVR

import logging


class EyeTrackVRDataSource(DataSource):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.eyetrackvr = EyeTrackVR()
        self.logger.info("initialized")

    def start(self):
        self.eyetrackvr.start()
        self.logger.info("started")

    def stop(self):
        self.eyetrackvr.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        x, y = self.eyetrackvr.get_last_data()
        next_vector = (x, y) if x and y else None
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
