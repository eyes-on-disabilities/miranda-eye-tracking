from typing import Optional

from data_sources.clients.mediapipe_lib import HeadTracker
from data_sources.data_source import DataSource
from misc import Vector


class MediaPipeDataSource(DataSource):
    def __init__(self, root_window):
        self.mediapipe = HeadTracker(root_window)

    def start(self):
        self.mediapipe.start()

    def stop(self):
        self.mediapipe.stop()

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.mediapipe.get_latest_data()
        return (last_data["yaw_deg"], last_data["pitch_deg"]) if last_data else None
