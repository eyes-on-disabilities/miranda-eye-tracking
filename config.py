import os
import sys
from misc import resource_path

# meta
APP_SHORT_NAME = "Miranda"
APP_FULL_NAME = "Miranda Eye-Tracking"
APP_VERSION = "0.1.0"
APP_ICON_LINUX = resource_path("assets/icon.png")
APP_ICON_WINDOWS = resource_path("assets/icon.ico")
APP_DESCRIPTION = "An eye-tracking-toolkit for calibrating eye- and head-tracker inputs to match your screen gaze."
APP_LINK_WEBSITE = "https://eyes-on-disabilities.org/"
APP_LINK_CODE = "https://codeberg.org/eyes-on-disabilities/miranda-eye-tracking"
APP_RELEASE_NOTES = """
Hello, and Welcome to Miranda.

This software is in an early stage of development. Expect things to not work properly, or to be insufficiently documented, or to simply look bad. We're working on it.

Nevertheless, we are very happy that you are using Miranda. If you have any questions or would even like to help, please feel free to contact us!

Your Eyes-on-Disabilities Team
"""

_LINUX_CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    APP_SHORT_NAME,
)
_WINDOWS_CONFIG_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    APP_SHORT_NAME,
)
CONFIG_DIR = _WINDOWS_CONFIG_DIR if sys.platform.startswith("win") else _LINUX_CONFIG_DIR
# ensure config directory exists:
os.makedirs(CONFIG_DIR, exist_ok=True)


# in application
MOUSE_SPEED_IN_PX = 20
LOOP_SLEEP_IN_MILLISEC = 100
SHOW_FINAL_CALIBRATION_TEXT_FOR_SEC = 30
SHOW_PREP_CALIBRATION_TEXT_FOR_SEC = 10
WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC = 3
VECTOR_COLLECTION_TIME_IN_SEC = 3
