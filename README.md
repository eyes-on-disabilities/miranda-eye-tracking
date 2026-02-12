# Miranda – The Eye Tracking Toolkit

![Two applications running. One is AITrack, which tracks the head position and rotation. The other is Miranda, receiving the data and calibrating it against the screen.](assets/README_hero.png)

Miranda is a toolkit for calibrating eye- and head-tracker inputs to match your screen gaze. It enables seamless integration with other applications, allowing you to use your calibrated tracker data in various ways.

For example, you can use Opentrack as an input source, calibrate your head rotation to your screen, and output the data as UDP messages. This enables you to control applications like OptiKey with your head movements.

> [!NOTE]  
> This software is early in development. Expect things to not work. We're very happy for your feedback and support!

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

In short, an _input method_ provides eye-tracking data, this data will be translated into screen coordinates using a _tracking approach_, and these coordinates will be used or publishes using an _output method_. Every input method and tracking approach combination needs a calibration first.

### Input Method
An _input method_ is where eye- and head-tracking data comes from. The data could be the yaw and pitch rotation of your eyes in degrees. An input method may be an integrated functionality of Miranda, or may be an external application that needs to run alongside Miranda. Since the data itself gives no indication of where the user is looking at we need a _tracking approach_.

### Tracking Approach
A _tracking approach_ tells how the data from an input method shall be translated into screen coordinates – a position on the screen, e.g. where a mouse cursor could move to. There are two approaches:

- **Gaze on Screen**: The user is directly looking at the screen. The eye movement directly translates to a screen position. This is the most straight-forward approach.
- **D-Pad**: This approach is a good alternative if your input is not accurate enough for the _Gaze on Screen_ approach. Usually, a D-pad is a flat, typically thumb-operated, directional control. Likewise with this approach the current screen coordinates is steered by looking at a d-pad. E.g. by looking at the "up" arrow, the screen coordinates moves up.

### Calibration
Before we can translate the data from the input method into screen coordinates, we need to do a calibration first. Every input method and tracking approach combination needs its own calibration. Once such a calibration is done the result will be stored and is available on the next start of Miranda.

### Output Methods
_Output methods_ take the screen coordinates created by the tracking approach and make use of them. Such a method could simply push the coordinates via UDP, like with the _UDP-Publisher_. Or it could be a whole tool, like a TTS keyboard.

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
