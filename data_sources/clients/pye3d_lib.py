import threading
import time
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from pupil_detectors import Detector2D
from pye3d.detector_3d import CameraModel, Detector3D, DetectorMode


class EyeTracker:
    def __init__(self, root, source=2, focal_length=1000.0, resolution=(640, 480)):
        self.root = root
        self.source = source
        self.detector_2d = Detector2D()
        self.camera = CameraModel(focal_length=focal_length, resolution=list(resolution))
        self.detector_3d = Detector3D(camera=self.camera, long_term_mode=DetectorMode.blocking)

        self._video_capture = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_result_3d = None
        self._latest_frame = None
        self._photo = None

        self.window = tk.Toplevel(self.root)
        self.window.title("Eye Tracker")
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)  # disable X button

        self.label = tk.Label(self.window)
        self.label.pack(fill="both", expand=True)

        self.root.after(0, self._update_tk_image)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

        thread = self._thread
        if thread is not None:
            thread.join()

        if self._video_capture is not None:
            self._video_capture.release()
            self._video_capture = None

        if self.window.winfo_exists():
            self.window.destroy()

    def get_latest_data(self):
        with self._lock:
            return self._latest_result_3d

    def _capture_loop(self):
        try:
            src = int(self.source)
        except ValueError:
            src = self.source

        self._video_capture = cv2.VideoCapture(src)

        while self._running and self._video_capture.isOpened():
            frame_number = self._video_capture.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self._video_capture.get(cv2.CAP_PROP_FPS) or 24
            ret, eye_frame = self._video_capture.read()
            if not ret:
                break

            gray = cv2.cvtColor(eye_frame, cv2.COLOR_BGR2GRAY)
            result_2d = self.detector_2d.detect(gray)
            result_2d["timestamp"] = frame_number / fps
            result_2d["method"] = "2d c++"
            result_3d = self.detector_3d.update_and_detect(result_2d, gray)

            ellipse_3d = result_3d["ellipse"]
            projected_sphere = result_3d["projected_sphere"]

            cv2.ellipse(
                eye_frame,
                tuple(int(v) for v in ellipse_3d["center"]),
                tuple(int(v / 2) for v in ellipse_3d["axes"]),
                ellipse_3d["angle"],
                0,
                360,
                (0, 255, 0),
            )
            cv2.ellipse(
                eye_frame,
                tuple(int(v) for v in projected_sphere["center"]),
                tuple(int(v / 2) for v in projected_sphere["axes"]),
                ellipse_3d["angle"],
                0,
                360,
                (255, 0, 0),
            )

            with self._lock:
                self._latest_result_3d = result_3d
                self._latest_frame = eye_frame.copy()

            if fps and fps > 0:
                time.sleep(1.0 / fps)
            else:
                time.sleep(0.04)

        self._running = False

    def _update_tk_image(self):
        if not self.window.winfo_exists():
            return

        frame = None
        with self._lock:
            if self._latest_frame is not None:
                frame = self._latest_frame.copy()

        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self._photo = ImageTk.PhotoImage(image=img)
            self.label.configure(image=self._photo)

        self.root.after(15, self._update_tk_image)
