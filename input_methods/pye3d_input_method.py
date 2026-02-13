from typing import Optional

from input_methods.clients.pye3d_client import Pye3DClient
from input_methods.input_method import DataSource
from misc import Vector

import logging


class Pye3dDataSource(DataSource):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pye3d = Pye3DClient(root_window)
        self.logger.info("initialized")

    def start(self):
        self.pye3d.start()
        self.logger.info("started")

    def stop(self):
        self.pye3d.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.pye3d.get_latest_data()
        next_vector = (last_data["theta"],
                       last_data["phi"]) if last_data else None
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
