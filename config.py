import os
import sys
from misc import resource_path

# meta
APP_SHORT_NAME = "Miranda"
APP_FULL_NAME = "Miranda Eye Tracking"
APP_VERSION = "1.0.0-alpha.1"
APP_ICON_LINUX = resource_path("assets/icon.png")
APP_ICON_WINDOWS = resource_path("assets/icon.ico")
APP_DESCRIPTION = "An eye-tracking-toolkit for calibrating eye- and head-tracker inputs to match your screen gaze."
APP_LINK_WEBSITE = "https://eyes-on-disabilities.org/"
APP_LINK_CODE = "https://codeberg.org/eyes-on-disabilities/miranda-eye-tracking"

LINUX_CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    APP_SHORT_NAME,
)

WINDOWS_CONFIG_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    APP_SHORT_NAME,
)

# in application
MOUSE_SPEED_IN_PX = 20
LOOP_SLEEP_IN_MILLISEC = 100
SHOW_FINAL_CALIBRATION_TEXT_FOR_SEC = 30
SHOW_PREP_CALIBRATION_TEXT_FOR_SEC = 10
WAIT_TIME_BEFORE_COLLECTING_VECTORS_IN_SEC = 3
VECTOR_COLLECTION_TIME_IN_SEC = 3
