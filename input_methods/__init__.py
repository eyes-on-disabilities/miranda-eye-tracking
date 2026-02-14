from input_methods.mediapipe_input_method import MediaPipeInputMethod
# Keep this import on top.
# There are some DLL loading issues with Mediapipe on Windows when loaded later,
# especially when together with opencv.
# See:
# https://github.com/google-ai-edge/mediapipe/issues/1905

from input_methods.mouse_input_method import MouseInputMethod
from input_methods.opentrack_input_method import OpentrackInputMethod
from input_methods.orlosky_input_method import OrloskyInputMethod
from input_methods.pupil_input_method import PupilInputMethod
from input_methods.pye3d_input_method import Pye3dInputMethod
from guis.tkinter.main_menu_window import MainMenuOption
from misc import resource_path
from input_methods.eyetrackvr_input_method import EyeTrackVRInputMethod

input_methods: dict[MainMenuOption] = {
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Position",
        description="The mouse position as input. Great for testing.",
        icon=resource_path("assets/input_method_mouse.png"),
        clazz=MouseInputMethod,
    ),
    "eye-tracking-glasses": MainMenuOption(
        key="eye-tracking-glasses",
        title="Eye-Tracking Glasses",
        description="Eye-Tracking using \"Eye-Tracking glasses\"\n" +
                    "with an infrared camera in front of the eye.",
        icon=resource_path("assets/input_method_eye-tracking-glasses.png"),
        clazz=Pye3dInputMethod,
    ),
    "webcam-head-tracking": MainMenuOption(
        key="webcam-head-tracking",
        title="Webcam Head-Tracking",
        description="Head-Tracking with just using a Webcam.",
        icon=resource_path("assets/input_method_webcam-head-tracking.png"),
        clazz=MediaPipeInputMethod,
    ),
    "opentrack": MainMenuOption(
        key="opentrack",
        title="OpenTrack",
        description="The rotation of your head with OpenTrack.\n" +
                    "**Requires an external application to work.**",
        icon=resource_path("assets/input_method_opentrack.png"),
        clazz=OpentrackInputMethod,
    ),
    "pupil": MainMenuOption(
        key="pupil",
        title="Pupil",
        description="Pupil Lab's 3d-eye detection.\n" +
                    "**Requires an external application to work.**",
        icon=resource_path("assets/input_method_pupil.png"),
        clazz=PupilInputMethod,
    ),
    "eyetrackvr": MainMenuOption(
        key="eyetrackvr",
        title="EyeTrackVR",
        description="Eye tracking with EyeTrackVR.\n" +
                    "**Requires an external application to work.**",
        icon=resource_path("assets/input_method_eyetrackvr.png"),
        clazz=EyeTrackVRInputMethod,
    ),
    "orlosky": MainMenuOption(
        key="orlosky",
        title="Orlosky",
        description="The 3DEyeTracker from Jason Orlosky.\n" +
                    "**Requires an external application to work.**",
        icon=resource_path("assets/input_method_orlosky.png"),
        clazz=OrloskyInputMethod,
    ),
}
