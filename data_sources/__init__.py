from data_sources.mediapipe_data_source import MediaPipeDataSource
# Keep this import on top.
# There are some DLL loading issues with Mediapipe on Windows when loaded later,
# especially when together with opencv.
# See:
# https://github.com/google-ai-edge/mediapipe/issues/1905

from data_sources.mouse_data_source import MouseDataSource
from data_sources.opentrack_data_source import OpentrackDataSource
from data_sources.orlosky_data_source import OrloskyDataSource
from data_sources.pupil_data_source import PupilDataSource
from data_sources.pye3d_data_source import Pye3dDataSource
from guis.tkinter.main_menu_window import MainMenuOption
from misc import resource_path
from data_sources.eyetrackvr_data_source import EyeTrackVRDataSource
from data_sources.opentrack_and_pupil_data_source import OpentrackAndPupilDataSource

data_sources: dict[MainMenuOption] = {
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Position",
        description="The mouse position as input. Great for testing.",
        icon=resource_path("assets/data_source_mouse.png"),
        clazz=MouseDataSource,
    ),
    "orlosky": MainMenuOption(
        key="orlosky",
        title="Orlosky",
        description="The 3DEyeTracker from Jason Orlosky.",
        icon=resource_path("assets/data_source_orlosky.png"),
        clazz=OrloskyDataSource,
    ),
    "opentrack": MainMenuOption(
        key="opentrack",
        title="OpenTrack",
        description="The rotation of your head with OpenTrack.",
        icon=resource_path("assets/data_source_opentrack.png"),
        clazz=OpentrackDataSource,
    ),
    "pupil": MainMenuOption(
        key="pupil",
        title="Pupil",
        description="Pupil Lab's 3d-eye detection.",
        icon=resource_path("assets/data_source_pupil.png"),
        clazz=PupilDataSource,
    ),
    "eyetrackvr": MainMenuOption(
        key="eyetrackvr",
        title="EyeTrackVR",
        description="Eye tracking with EyeTrackVR.",
        icon=resource_path("assets/data_source_eyetrackvr.png"),
        clazz=EyeTrackVRDataSource,
    ),
    "pye3d": MainMenuOption(
        key="pye3d",
        title="Pye3d",
        description="Integrated Eye-Tracking using pye3D.",
        icon=resource_path("assets/data_source_pupil.png"),
        clazz=Pye3dDataSource,
    ),
    "mediapipe": MainMenuOption(
        key="mediapipe",
        title="MediaPipe",
        description="Integrated Head-Tracking using MediaPipe.",
        icon=resource_path("assets/data_source_pupil.png"),
        clazz=MediaPipeDataSource,
    ),
}
