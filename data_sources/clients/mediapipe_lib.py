import threading
import time
import math
from collections import deque

import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


COLOR_VIOLET = (134, 42, 161)
COLOR_YELLOW = (0, 237, 254)


class HeadTracker:
    @staticmethod
    def detect_cameras(max_cams=10):
        available_cameras = []
        for i in range(max_cams):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
            cap.release()
        return available_cameras

    def __init__(self, root, source=0, resolution=(640, 480), max_cams=10, filter_length=8):
        self.root = root
        self.resolution = resolution
        self.filter_length = filter_length

        self._video_capture = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_data = None
        self._latest_frame = None
        self._photo = None

        self._cameras = self.detect_cameras(max_cams=max_cams)
        self._requested_source = None
        self._source_changed = False

        self._mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.FACE_OUTLINE_INDICES = [
            10, 338, 297, 332, 284, 251, 389, 356,
            454, 323, 361, 288, 397, 365, 379, 378,
            400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21,
            54, 103, 67, 109
        ]
        self.LANDMARKS = {
            "left": 234,
            "right": 454,
            "top": 10,
            "bottom": 152,
            "front": 1,
        }

        self._ray_origins = deque(maxlen=self.filter_length)
        self._ray_directions = deque(maxlen=self.filter_length)

        self.window = tk.Toplevel(self.root)
        self.window.title("Head Tracker")
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

        self.label = tk.Label(self.window)
        self.label.pack(side="top", fill="both", expand=True)

        self._init_camera_selection(source)
        self.root.after(0, self._update_tk_image)

    def _init_camera_selection(self, source):
        values = [str(i) for i in self._cameras]
        if values:
            self.cam_combo["values"] = values
            chosen = str(source) if str(source) in values else values[0]
            self.cam_var.set(chosen)
            self._set_requested_source(int(chosen), force=True)
        else:
            self.cam_combo["values"] = ["None"]
            self.cam_var.set("None")
            self.cam_combo.state(["disabled"])
            self._set_requested_source(None, force=True)

    def _on_camera_selected(self, _event=None):
        val = self.cam_var.get()
        if val == "None":
            self._set_requested_source(None)
            return
        try:
            self._set_requested_source(int(val))
        except ValueError:
            self._set_requested_source(None)

    def _set_requested_source(self, src, force=False):
        with self._lock:
            if force or self._requested_source != src:
                self._requested_source = src
                self._source_changed = True
        self._ray_origins.clear()
        self._ray_directions.clear()

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

        try:
            self._face_mesh.close()
        except Exception:
            pass

        if self.window.winfo_exists():
            self.window.destroy()

    def get_latest_data(self):
        with self._lock:
            return self._latest_data

    @staticmethod
    def _landmark_to_np(landmark, w, h):
        return np.array([landmark.x * w, landmark.y * h, landmark.z * w], dtype=np.float32)

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
                    self._latest_data = None
                    self._latest_frame = None
                time.sleep(0.05)
                continue

            ret, frame = self._video_capture.read()
            if not ret or frame is None:
                try:
                    self._video_capture.release()
                finally:
                    self._video_capture = None
                with self._lock:
                    self._latest_data = None
                    self._latest_frame = None
                time.sleep(0.05)
                continue

            try:
                h, w, _ = frame.shape
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self._face_mesh.process(rgb)

                data = None

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0].landmark

                    # draw landmarks OVER camera frame (not on a blank debug canvas)
                    for i, lm in enumerate(face_landmarks):
                        pt = self._landmark_to_np(lm, w, h)
                        x, y = int(pt[0]), int(pt[1])
                        if 0 <= x < w and 0 <= y < h:
                            cv2.circle(frame, (x, y), 2, COLOR_VIOLET, -1)

                    # key points
                    key_points = {}
                    for name, idx in self.LANDMARKS.items():
                        pt = self._landmark_to_np(face_landmarks[idx], w, h)
                        key_points[name] = pt

                    left = key_points["left"]
                    right = key_points["right"]
                    top = key_points["top"]
                    bottom = key_points["bottom"]
                    front = key_points["front"]

                    right_axis = (right - left)
                    right_axis /= (np.linalg.norm(right_axis) + 1e-8)

                    up_axis = (top - bottom)
                    up_axis /= (np.linalg.norm(up_axis) + 1e-8)

                    forward_axis = np.cross(right_axis, up_axis)
                    forward_axis /= (np.linalg.norm(forward_axis) + 1e-8)
                    forward_axis = -forward_axis

                    center = (left + right + top + bottom + front) / 5.0

                    half_width = np.linalg.norm(right - left) / 2.0
                    half_height = np.linalg.norm(top - bottom) / 2.0
                    half_depth = 80.0

                    def corner(x_sign, y_sign, z_sign):
                        return (
                            center
                            + x_sign * half_width * right_axis
                            + y_sign * half_height * up_axis
                            + z_sign * half_depth * forward_axis
                        )

                    def project(pt3d):
                        return int(pt3d[0]), int(pt3d[1])

                    self._ray_origins.append(center)
                    self._ray_directions.append(forward_axis)

                    avg_origin = np.mean(self._ray_origins, axis=0)
                    avg_direction = np.mean(self._ray_directions, axis=0)
                    avg_direction /= (np.linalg.norm(avg_direction) + 1e-8)

                    reference_forward = np.array([0, 0, -1], dtype=np.float32)

                    xz_proj = np.array(
                        [avg_direction[0], 0, avg_direction[2]], dtype=np.float32)
                    xz_proj /= (np.linalg.norm(xz_proj) + 1e-8)
                    yaw_rad = math.acos(
                        float(np.clip(np.dot(reference_forward, xz_proj), -1.0, 1.0)))
                    if avg_direction[0] < 0:
                        yaw_rad = -yaw_rad

                    yz_proj = np.array(
                        [0, avg_direction[1], avg_direction[2]], dtype=np.float32)
                    yz_proj /= (np.linalg.norm(yz_proj) + 1e-8)
                    pitch_rad = math.acos(
                        float(np.clip(np.dot(reference_forward, yz_proj), -1.0, 1.0)))
                    if avg_direction[1] > 0:
                        pitch_rad = -pitch_rad

                    yaw_deg = float(np.degrees(yaw_rad))
                    pitch_deg = float(np.degrees(pitch_rad))

                    if yaw_deg < 0:
                        yaw_deg = abs(yaw_deg)
                    elif yaw_deg < 180:
                        yaw_deg = 360 - yaw_deg

                    if pitch_deg < 0:
                        pitch_deg = 360 + pitch_deg

                    ray_length = 2.5 * half_depth
                    ray_end = avg_origin - avg_direction * ray_length
                    cv2.line(frame, project(avg_origin),
                             project(ray_end), COLOR_YELLOW, 3)

                    data = {
                        "timestamp": time.time(),
                        "center": avg_origin.astype(float).tolist(),
                        "direction": avg_direction.astype(float).tolist(),
                        "yaw_deg": yaw_deg,
                        "pitch_deg": pitch_deg,
                        "raw": {
                            "center": center.astype(float).tolist(),
                            "direction": forward_axis.astype(float).tolist(),
                        },
                    }

                with self._lock:
                    self._latest_data = data
                    self._latest_frame = frame.copy()

            except Exception:
                with self._lock:
                    self._latest_data = None
                    self._latest_frame = None
                time.sleep(0.02)
                continue

            time.sleep(0.01)

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
