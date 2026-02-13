import threading
import time
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pupil_detectors import Detector2D
from pye3d.detector_3d import CameraModel, Detector3D, DetectorMode

import logging


COLOR_VIOLET = (134, 42, 161)
COLOR_YELLOW = (0, 237, 254)


class Pye3DClient:
    @staticmethod
    def detect_cameras(max_cams=10):
        available_cameras = []
        for i in range(max_cams):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
            cap.release()
        return available_cameras

    def __init__(self, root, source=0, focal_length=1000.0, resolution=(640, 480), max_cams=10):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root = root
        self.detector_2d = Detector2D()
        self.camera = CameraModel(
            focal_length=focal_length, resolution=list(resolution))
        self.detector_3d = Detector3D(
            camera=self.camera, long_term_mode=DetectorMode.blocking)

        self._video_capture = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_result_3d = None
        self._latest_frame = None
        self._photo = None

        self._cameras = self.detect_cameras(max_cams=max_cams)

        self._requested_source = None
        self._source_changed = False

        self.window = tk.Toplevel(self.root)
        self.window.title("Eye Tracker")
        self.window.geometry("500x500+0+0")
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)

        self.top_bar = ttk.Frame(self.window)
        self.top_bar.pack(side="top", fill="x")

        ttk.Label(self.top_bar, text="Camera:").pack(
            side="left", padx=(8, 6), pady=8)

        self.cam_var = tk.StringVar()
        self.cam_combo = ttk.Combobox(
            self.top_bar, state="readonly", textvariable=self.cam_var)
        self.cam_combo.pack(side="left", fill="x",
                            expand=True, padx=(0, 8), pady=8)
        self.cam_combo.bind("<<ComboboxSelected>>", self._on_camera_selected)

        self.reset_button = ttk.Button(
            self.window,
            text="Reset eye ball",
            command=self._reset_eyeball,
        )
        self.reset_button.pack(side="top", fill="x", padx=8, pady=(0, 8))

        self.label = tk.Label(self.window)
        self.label.pack(side="top", fill="both", expand=True)

        self._init_camera_selection(source)
        self.root.after(0, self._update_tk_image)
        self.logger.debug("initialized")

    def _reset_eyeball(self):
        try:
            self.detector_3d.reset()
        except Exception:
            pass

    def _init_camera_selection(self, source):
        values = [str(i) for i in self._cameras]
        if values:
            self.cam_combo["values"] = values
            chosen = str(source) if str(source) in values else values[0]
            self.cam_var.set(chosen)
            self._set_requested_source(int(chosen), force=True)
            self._reset_eyeball()
        else:
            self.cam_combo["values"] = ["None"]
            self.cam_var.set("None")
            self.cam_combo.state(["disabled"])
            self._set_requested_source(None, force=True)
            self._reset_eyeball()

    def _on_camera_selected(self, _event=None):
        val = self.cam_var.get()
        if val == "None":
            self._set_requested_source(None)
            self._reset_eyeball()
            return
        try:
            self._set_requested_source(int(val))
        except ValueError:
            self._set_requested_source(None)
        self._reset_eyeball()

    def _set_requested_source(self, src, force=False):
        with self._lock:
            if force or self._requested_source != src:
                self._requested_source = src
                self._source_changed = True

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        self.logger.debug("started")

    def stop(self):
        self._running = False

        try:
            thread = self._thread
            if thread is not None:
                thread.join()

            if self._video_capture is not None:
                self._video_capture.release()
                self._video_capture = None

            if self.window.winfo_exists():
                self.root.after(0, self.window.destroy)

        except tk.TclError:
            self.logger.warning("Tkinter window was already closed.")
        except Exception:
            self.logger.exception("")

        self.logger.debug("stopped")

    def get_latest_data(self):
        with self._lock:
            return self._latest_result_3d

    def _apply_source_change_if_needed(self):
        with self._lock:
            changed = self._source_changed
            src = self._requested_source
            if changed:
                self._source_changed = False

        if not changed:
            return

        if self._video_capture is not None:
            try:
                self._video_capture.release()
            finally:
                self._video_capture = None

        if src is None:
            return

        cap = cv2.VideoCapture(int(src))
        if cap.isOpened():
            self._video_capture = cap
        else:
            cap.release()
            self._video_capture = None

    def _try_open_requested_source(self):
        with self._lock:
            src = self._requested_source

        if src is None:
            return False

        cap = cv2.VideoCapture(int(src))
        if cap.isOpened():
            if self._video_capture is not None:
                try:
                    self._video_capture.release()
                finally:
                    self._video_capture = None
            self._video_capture = cap
            return True

        cap.release()
        return False

    def _capture_loop(self):
        last_retry = 0.0

        while self._running:
            self._apply_source_change_if_needed()

            if self._video_capture is None or not self._video_capture.isOpened():
                now = time.time()
                if now - last_retry >= 0.5:
                    last_retry = now
                    self._try_open_requested_source()

                with self._lock:
                    self._latest_result_3d = None
                    self._latest_frame = None
                time.sleep(0.05)
                continue

            ret, eye_frame = self._video_capture.read()
            if not ret or eye_frame is None:
                try:
                    self._video_capture.release()
                finally:
                    self._video_capture = None

                with self._lock:
                    self._latest_result_3d = None
                    self._latest_frame = None

                time.sleep(0.05)
                continue

            fps = self._video_capture.get(cv2.CAP_PROP_FPS) or 24.0
            frame_number = self._video_capture.get(cv2.CAP_PROP_POS_FRAMES)

            try:
                gray = cv2.cvtColor(eye_frame, cv2.COLOR_BGR2GRAY)
                result_2d = self.detector_2d.detect(gray)

                if result_2d is None:
                    with self._lock:
                        self._latest_result_3d = None
                        self._latest_frame = eye_frame.copy()
                    time.sleep(0.01)
                    continue

                result_2d["timestamp"] = frame_number / \
                    fps if fps and fps > 0 else time.time()
                result_2d["method"] = "2d c++"

                result_3d = self.detector_3d.update_and_detect(result_2d, gray)

                if result_3d is None:
                    with self._lock:
                        self._latest_result_3d = None
                        self._latest_frame = eye_frame.copy()
                    time.sleep(0.01)
                    continue

                ellipse_3d = result_3d.get("ellipse")
                projected_sphere = result_3d.get("projected_sphere")

                if ellipse_3d and "center" in ellipse_3d and "axes" in ellipse_3d:
                    cv2.ellipse(
                        eye_frame,
                        tuple(int(v) for v in ellipse_3d["center"]),
                        tuple(int(v / 2) for v in ellipse_3d["axes"]),
                        ellipse_3d.get("angle", 0.0),
                        0,
                        360,
                        COLOR_YELLOW,
                        thickness=3,
                    )

                if projected_sphere and "center" in projected_sphere and "axes" in projected_sphere:
                    cv2.ellipse(
                        eye_frame,
                        tuple(int(v) for v in projected_sphere["center"]),
                        tuple(int(v / 2) for v in projected_sphere["axes"]),
                        (ellipse_3d or {}).get("angle", 0.0),
                        0,
                        360,
                        COLOR_VIOLET,
                        thickness=3,
                    )

                with self._lock:
                    self._latest_result_3d = result_3d
                    self._latest_frame = eye_frame.copy()

            except Exception:
                with self._lock:
                    self._latest_result_3d = None
                    self._latest_frame = None
                time.sleep(0.02)
                continue

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

            w = self.label.winfo_width()
            h = self.label.winfo_height()
            if w > 1 and h > 1:
                img = img.resize((w, h), Image.Resampling.LANCZOS)

            self._photo = ImageTk.PhotoImage(image=img)
            self.label.configure(image=self._photo)

        self.root.after(15, self._update_tk_image)
