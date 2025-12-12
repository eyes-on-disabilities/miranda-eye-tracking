from typing import Optional

from data_sources.clients.pye3d_lib import EyeTracker
from data_sources.data_source import DataSource
from misc import Vector


class Pye3dDataSource(DataSource):
    def __init__(self, root_window):
        self.pye3d = EyeTracker(root_window)

    def start(self):
        self.pye3d.start()

    def stop(self):
        self.pye3d.stop()

    def get_next_vector(self) -> Optional[Vector]:
        last_data = self.pye3d.get_latest_data()
        return (last_data["theta"], last_data["phi"]) if last_data else None
