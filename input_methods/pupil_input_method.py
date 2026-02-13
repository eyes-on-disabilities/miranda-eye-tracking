from typing import Optional

from input_methods.clients.pupil_client import PupilClient
from input_methods.input_method import InputMethod
from misc import Vector

import logging


class PupilInputMethod(InputMethod):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pupil = PupilClient()
        self.logger.info("initialized")

    def start(self):
        self.pupil.start()
        self.logger.info("started")

    def stop(self):
        self.pupil.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.pupil.get_last_data()["3d"]
        next_vector = (last_data["theta"],
                       last_data["phi"]) if last_data else None
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
