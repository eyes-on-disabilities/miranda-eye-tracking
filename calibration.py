import csv
import os
import sys
from typing import List

import config
from misc import Vector


class CalibrationInstruction:
    """An instruction for a GUI for what to display when calibrating.
    If a vector is given, it represents the display. To be independent from any screen resolutions,
    the vector shall just have a value range of -1.0<=x<=1.0 and 1.0>=y>=-1.0.
    E.g. (-1.0,1.0) is the upper left corner of the screen, and (-1.0,-1.0) is the lower right corner."""

    def __init__(self, vector: Vector = None, text: str = None, image: str = None):
        self.vector = vector
        self.text = text
        self.image = image


class CalibrationInstructions:
    def __init__(self, preparational_text: str, instructions: list[CalibrationInstruction]):
        self.preparational_text = preparational_text
        self.instructions = instructions


class CalibrationResult:
    def __init__(self, vectors: List[Vector]):
        self.vectors = vectors


base_dir = config.WINDOWS_CONFIG_DIR if sys.platform.startswith("win") else config.LINUX_CONFIG_DIR
directory = os.path.join(base_dir, "calibration_results")
file_format = os.path.join(directory, "{}_{}.csv")


def _ensure_dirs():
    os.makedirs(directory, exist_ok=True)


def has_result(data_source: str, tracking_approach: str) -> bool:
    return os.path.exists(file_format.format(data_source, tracking_approach))


def load_result(data_source: str, tracking_approach: str) -> CalibrationResult:
    vectors = []
    with open(file_format.format(data_source, tracking_approach), "r") as f:
        for row in csv.reader(f):
            vectors.append((float(row[0]), float(row[1])))  # Convert strings to floats
    return CalibrationResult(vectors)


def save_result(data_source: str, tracking_approach: str, calibration_result: CalibrationResult):
    _ensure_dirs()
    with open(file_format.format(data_source, tracking_approach), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(calibration_result.vectors)


def delete_result(data_source: str, tracking_approach: str):
    config_file = file_format.format(data_source, tracking_approach)
    if os.path.exists(config_file):
        os.remove(config_file)
