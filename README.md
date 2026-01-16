# Miranda – The Eye Tracking Screen Calibrator

![Two applications running. One is AITrack, which tracks the head position and rotation. The other is Miranda, receiving the data and calibrating it against the screen.](assets/README_hero.png)

Miranda is a GUI tool for calibrating eye and head tracker input to match your screen gaze. It enables seamless integration with other applications, allowing you to use your calibrated tracker data in various ways.

For example, you can use Opentrack as an input source, calibrate your head rotation to your screen, and output the data as UDP messages. This enables you to control applications like OptiKey with your head movements.

## Prerequisites for Linux

On Linux systems, install [espeak-ng](https://github.com/espeak-ng/espeak-ng):
```
apt install espeak-ng
```
This is not needed for Windows.

## Run Miranda

Python 3.11.14 is suggested.
Load the dependencies and run `main.py`:
```
pip install -r requirements.txt
python main.py
```

Alternatively, you may also use [uv](https://docs.astral.sh/uv/getting-started/installation/) to run Miranda:
```
uv run --with-requirements requirements.txt main.py [miranda args]
```

## Build .exe on Windows
```
pip install PyInstaller
PyInstaller .\Miranda.spec
```

## Concepts

In short, data comes from a _data source_, this data will be translated into mouse movements using a _tracking approach_, and these mouse movements will be _published_ for further usage. Every data source and tracking approach combination needs a calibration first.

### Data Source
A _data source_ is where eye and head tracking data comes from. The data could be the yaw and pitch rotation of your eyes in degrees. The data source is mostly a different application, that needs to run alongside Miranda. Since the data itself gives no indication of where the user is looking at or how the mouse cursor shall be moved, we need a _tracking approach_.

### Tracking Approach
A _tracking approach_ tells how the data from the data source shall be translated into a mouse movement. There are two approaches:

- **Gaze on Screen**: The user is directly looking at the screen. The cursor shall follow the gaze. This is the most straight-forward and probably mostly used approach.
- **D-Pad**: This approach is a good alternative if your input device is not accurate enough for the _Gaze on Screen_ approach. Usually, a D-pad is a flat, typically thumb-operated, directional control. Likewise with this approach the cursor is looking at a d-pad to steer the cursor. E.g. by looking at the "up" arrow, the cursor moves up.

### Calibration
Before we can translate the data from the data source into mouse movements, we need to do a calibration first. Every data source and tracking approach combination needs its own calibration. Once such a calibration is done the result will be stored and is available on the next start of Miranda.

### Publishers
_Publishers_ take the mouse movements created by the tracking approach and publish them for further usage of other applications. Currently there is just the _UDP-Publisher_, which publishes the mouse coordinates via UDP to 127.0.0.1 port 9999 in the following format:
```
# example
{"x": 173, "y": 432, "timestamp": "2024-11-14 00:56:42.308879"}
```

## Open Source License Attribution

This application uses Open Source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

### Libraries

#### [MediaPipe](https://ai.google.dev/edge/mediapipe)
* Copyright (c) The MediaPipe Authors
* [Apache License 2.0](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE)

#### [msgpack](https://msgpack.org/)
* Copyright (C) 2008-2011 INADA Naoki
* [Apache License 2.0](https://github.com/msgpack/msgpack-python/blob/main/COPYING)

#### [NumPy](https://numpy.org/)
* Copyright (c) 2005-2025 NumPy Developers
* [BSD 3-Clause License](https://github.com/numpy/numpy/blob/main/LICENSE.txt)

#### [opencv-python](https://pypi.org/project/opencv-python/)
* Copyright (c) Olli-Pekka Heinisuo
* [MIT License](https://github.com/opencv/opencv-python/blob/master/LICENSE.txt)

#### [pupil-detectors](https://github.com/pupil-labs/pupil-detectors)
* Copyright (c) Pupil Labs
* [LGPL-3.0 License](https://github.com/pupil-labs/pupil-detectors/blob/master/COPYING.LESSER)
* [GPL-3.0 License](https://github.com/pupil-labs/pupil-detectors/blob/master/COPYING)

#### [PyAutoGUI](https://github.com/asweigart/pyautogui)
* Copyright (c) 2014 Al Sweigart
* [BSD 3-Clause License](https://github.com/asweigart/pyautogui/blob/master/LICENSE.txt)

#### [pye3d](https://github.com/pupil-labs/pye3d-detector)
* Copyright (c) Pupil Labs
* [LGPL-3.0 License](https://github.com/pupil-labs/pye3d-detector/blob/master/LICENSE)

#### [python-osc](https://github.com/attwad/python-osc)
* Copyright (c) python-osc contributors
* [The Unlicense](https://github.com/attwad/python-osc/blob/main/LICENSE.txt)

#### [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
* Copyright (c) nateshmbhat and contributors
* [Mozilla Public License 2.0](https://github.com/nateshmbhat/pyttsx3/blob/master/LICENSE)

#### [screeninfo](https://github.com/rr-/screeninfo)
* Copyright (c) Marcin Kurczewski
* [MIT License](https://github.com/rr-/screeninfo/blob/master/LICENSE.md)

#### [PyZMQ](https://github.com/zeromq/pyzmq)
* Copyright (c) Brian E. Granger & Min Ragan-Kelley
* [BSD 3-Clause License](https://github.com/zeromq/pyzmq/blob/main/LICENSE.md)

### Others

#### [EyeTracker](https://github.com/JEOresearch/EyeTracker)
* Copyright (c) 2024 JEOresearch
* [MIT License](https://github.com/JEOresearch/EyeTracker/blob/main/LICENSE)
