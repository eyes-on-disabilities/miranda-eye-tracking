from misc import Vector
from typing import Optional
import pyautogui

from data_sources.data_source import DataSource

import logging


class MouseDataSource(DataSource):

    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("initialized")

    def start(self):
        self.logger.info("started")

    def stop(self):
        self.logger.info("stopped")

    def get_next_vector(self) -> Optional[Vector]:
        next_vector = pyautogui.position()
        self.logger.debug(f"next_vector: {next_vector}")
        return next_vector
