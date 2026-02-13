from abc import ABC, abstractmethod
from misc import Vector
from typing import Optional


class InputMethod(ABC):
    """Provides any kind of two-dimensional vector.
    This vector could be the coordinates of the mouse position
    or the rotation angles of an eye."""

    @abstractmethod
    def start(self):
        """Starts the InputMethod.
        Takes the root window in case a GUI needs to be displayed."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the InputMethod."""
        pass

    @abstractmethod
    def get_next_vector(self, timeout_in_ms: int) -> Optional[Vector]:
        """Gets the current vector, if one is available.
        Returns None if the InputMethod is not running or we hit the timeout."""
        pass
