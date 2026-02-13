from typing import Optional

from input_methods.clients.mediapipe_client import MediaPipeClient
from input_methods.input_method import DataSource
from misc import Vector

import logging


class MediaPipeDataSource(DataSource):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mediapipe = MediaPipeClient(root_window)
        self.logger.info("initialized")

    def start(self):
        self.mediapipe.start()
        self.logger.info("started")

    def stop(self):
        self.mediapipe.stop()
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.mediapipe.get_latest_data()
        next_vector = (last_data["yaw_deg"],
                       last_data["pitch_deg"]) if last_data else None
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
