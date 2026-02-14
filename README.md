# Miranda – The Eye Tracking Toolkit

![The application "Miranda" is shown, which enables an eye to control the mouse cursor movement. Two windows are shown. The left window shows camera footage with a close-up of a moving eye. Colored circles are drawn by the application around the eye and the pupil and indicate that the eye is tracked. The right window shows settings on how the eye movement shall be tracked and what shall be done with that movement. The "input" setting shows "Eye-Tracking Glasses", and the "output" setting shows "Mouse Movement". A mouse cursor moves around matchin the movement of the eye.](assets/README_hero.gif)

Miranda is a toolkit for calibrating eye- and head-tracker inputs to match your screen gaze. It enables integration with other applications, allowing you to use your calibrated tracker data in various ways.

For example, you can use live camera footage of your eye as an input, calibrate your eye movements to your screen, and then move the mouse cursor to the point you are looking at, or publish the position via UDP for further use.

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

## How it works

There are three components: _inputs_, _tracking approaches_, and _outputs_.
An _input_ provides eye-tracking data. This data is translated into screen coordinates using a _tracking approach_, and these coordinates are then used or published through an _output_. Each input and tracking approach combination requires prior calibration.

### Inputs
An _input_ is where eye- and head-tracking data comes from. The data could be the yaw and pitch rotation of your eyes in degrees. An input may be an integrated eye-tracking functionality of Miranda, or may be an external application that needs to run alongside Miranda. Since the data itself gives no indication of where the user is looking at we need a _tracking approach_.

The inputs are:

* Integrated Inputs:
  * **Mouse Position**: The mouse position as input. Great for testing.
  * **Eye-Tracking Glasses**: Eye-Tracking using "Eye-Tracking glasses" with an infrared camera in front of the eye.
  * **Webcam Head-Tracking**: Head-Tracking with just using a Webcam.
* Inputs requiring an external application:
  * [OpenTrack](https://github.com/opentrack/opentrack): The rotation of your head with OpenTrack.
  * [Pupil](https://docs.pupil-labs.com/core/): Pupil Lab's 3d-eye detection.
  * [EyeTrackVR](https://docs.eyetrackvr.dev/): Eye tracking with EyeTrackVR.
  * [Orlosky](https://github.com/JEOresearch/EyeTracker/tree/main): The 3DEyeTracker from Jason Orlosky.

### Tracking Approach
A _tracking approach_ tells how the data from an input method shall be translated into screen coordinates – a position on the screen, e.g. where a mouse cursor could move to.

There are two approaches:

* **Gaze on Screen**: The user is directly looking at the screen. The eye movement directly translates to a screen position. This is the most straight-forward approach.
* **D-Pad**: This approach is a good alternative if your input is not accurate enough for the _Gaze on Screen_ approach. Usually, a D-pad is a flat, typically thumb-operated, directional control. Likewise with this approach the current screen coordinates is steered by looking at a d-pad. E.g. by looking at the "up" arrow, the screen coordinates moves up.

### Calibration
Before we can translate the data from the input method into screen coordinates, we need to do a calibration first. Every input method and tracking approach combination needs its own calibration. Once such a calibration is done the result will be stored and is available on the next start of Miranda.

### Outputs
_Outputs_ take the screen coordinates created by the tracking approach and make use of them.

The outputs are:

* **UDP-Export**: Publish the gaze results over UDP in a simple JSON format.
* **Mouse Movement**: Moves the mouse cursor according to the gaze.
* **TTS Keyboard**: A text-to-speech-keyboard. (Proove-of-concept)

## Open Source License Attribution

This application uses open source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

### Libraries

* [MediaPipe](https://ai.google.dev/edge/mediapipe), Copyright (c) The MediaPipe Authors, [Apache License 2.0](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE)
* [msgpack](https://msgpack.org/), Copyright (C) 2008-2011 INADA Naoki, [Apache License 2.0](https://github.com/msgpack/msgpack-python/blob/main/COPYING)
* [NumPy](https://numpy.org/), Copyright (c) 2005-2025 NumPy Developers, [BSD 3-Clause License](https://github.com/numpy/numpy/blob/main/LICENSE.txt)
* [opencv-python](https://pypi.org/project/opencv-python/), Copyright (c) Olli-Pekka Heinisuo, [MIT License](https://github.com/opencv/opencv-python/blob/master/LICENSE.txt)
* [pupil-detectors](https://github.com/pupil-labs/pupil-detectors), Copyright (c) Pupil Labs, [LGPL-3.0 License](https://github.com/pupil-labs/pupil-detectors/blob/master/COPYING.LESSER) and [GPL-3.0 License](https://github.com/pupil-labs/pupil-detectors/blob/master/COPYING)
* [PyAutoGUI](https://github.com/asweigart/pyautogui), Copyright (c) 2014 Al Sweigart, [BSD 3-Clause License](https://github.com/asweigart/pyautogui/blob/master/LICENSE.txt)
* [pye3d](https://github.com/pupil-labs/pye3d-detector), Copyright (c) Pupil Labs, [LGPL-3.0 License](https://github.com/pupil-labs/pye3d-detector/blob/master/LICENSE)
* [python-osc](https://github.com/attwad/python-osc), Copyright (c) python-osc contributors, [The Unlicense](https://github.com/attwad/python-osc/blob/main/LICENSE.txt)
* [pyttsx3](https://github.com/nateshmbhat/pyttsx3), Copyright (c) nateshmbhat and contributors, [Mozilla Public License 2.0](https://github.com/nateshmbhat/pyttsx3/blob/master/LICENSE)
* [screeninfo](https://github.com/rr-/screeninfo), Copyright (c) Marcin Kurczewski, [MIT License](https://github.com/rr-/screeninfo/blob/master/LICENSE.md)
* [PyZMQ](https://github.com/zeromq/pyzmq), Copyright (c) Brian E. Granger & Min Ragan-Kelley, [BSD 3-Clause License](https://github.com/zeromq/pyzmq/blob/main/LICENSE.md)

### Others

* [EyeTracker](https://github.com/JEOresearch/EyeTracker), Copyright (c) 2024 JEOresearch, [MIT License](https://github.com/JEOresearch/EyeTracker/blob/main/LICENSE)

## License

Miranda is distributed under the terms of the [GPL version 3.0](LICENSE) or any later version.
