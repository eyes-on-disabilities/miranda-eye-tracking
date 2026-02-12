from typing import Optional

from input_methods.clients.orlosky import Orlosky
from input_methods.input_method import DataSource
from misc import Vector

import logging


class OrloskyDataSource(DataSource):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.orlosky = Orlosky()
        self.logger.info("initialized")

    def start(self):
        self.orlosky.start()
        self.logger.info("started")

    def stop(self):
        self.orlosky.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        next_vector = None

        last_data = self.orlosky.get_last_data()
        if last_data:
            x = last_data["x"]
            y = last_data["y"]
            z = last_data["z"]

            if z != 0:  # Avoid division by zero
                next_vector = (x / z, y / z)

        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
