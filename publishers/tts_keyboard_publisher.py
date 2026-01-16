from __future__ import annotations

import time
import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from misc import Vector, TTS
from publishers.publisher import Publisher

import logging


# ----------------------------
# Config
# ----------------------------

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 400

FILL_DURATION = 1.0
GRACE_DURATION = 0.6

BACKGROUND = "#333"
BASE_FILL = "#555"
PROGRESS_FILL = "#777"
OUTLINE = "#333"

KEY_TEXT_FILL = "white"
TEXT_TARGET_FILL = "#feed00"

KEY_FONT = ("TkDefaultFont", 26, "normal")
TEXT_FONT = ("TkDefaultFont", 20, "normal")

CURSOR_RADIUS = 10
CURSOR_FILL = "#a12a86"

Rect = Tuple[float, float, float, float]
RelRect = Tuple[float, float, float, float]


@dataclass
class Target:
    key: str
    rel_rect: RelRect
    text: str = ""
    on_trigger: Optional[Callable[[], None]] = None

    fill_duration_s: float = FILL_DURATION
    grace_duration_s: float = GRACE_DURATION

    base_fill: str = BASE_FILL
    progress_fill: str = PROGRESS_FILL
    outline: str = OUTLINE
    text_fill: str = KEY_TEXT_FILL
    font: Tuple[str, int, str] = KEY_FONT
    text_anchor: str = "center"
    text_padding: int = 14  # used if anchor == "w"

    base_id: Optional[int] = None
    progress_id: Optional[int] = None
    outline_id: Optional[int] = None
    text_id: Optional[int] = None

    progress: float = field(default=0.0, init=False)
    _inside: bool = field(default=False, init=False)
    _last_update: float = field(default=0.0, init=False)
    _last_exit: float = field(default=0.0, init=False)

    def layout(self, w: int, h: int) -> Rect:
        x1, y1, x2, y2 = self.rel_rect
        return (x1 * w, y1 * h, x2 * w, y2 * h)

    @staticmethod
    def contains(x: float, y: float, rect: Rect) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2

    def _text_pos(self, rect: Rect) -> tuple[float, float, str]:
        x1, y1, x2, y2 = rect
        if self.text_anchor == "w":
            return (x1 + self.text_padding, (y1 + y2) / 2, "w")
        return ((x1 + x2) / 2, (y1 + y2) / 2, "center")

    def draw(self, canvas: tk.Canvas, rect: Rect):
        x1, y1, x2, y2 = rect

        if self.base_id is None:
            self.base_id = canvas.create_rectangle(
                x1, y1, x2, y2, outline="", fill=self.base_fill)
        else:
            canvas.coords(self.base_id, x1, y1, x2, y2)

        fy2 = y2
        fy1 = y2 - (y2 - y1) * max(0.0, min(1.0, self.progress))
        if self.progress_id is None:
            self.progress_id = canvas.create_rectangle(
                x1, fy1, x2, fy2, outline="", fill=self.progress_fill)
        else:
            canvas.coords(self.progress_id, x1, fy1, x2, fy2)

        if self.outline_id is None:
            self.outline_id = canvas.create_rectangle(
                x1, y1, x2, y2, outline=self.outline, width=2, fill="")
        else:
            canvas.coords(self.outline_id, x1, y1, x2, y2)

        tx, ty, anchor = self._text_pos(rect)
        if self.text_id is None:
            self.text_id = canvas.create_text(
                tx, ty, text=self.text, fill=self.text_fill, font=self.font, anchor=anchor)
        else:
            canvas.coords(self.text_id, tx, ty)
            canvas.itemconfig(self.text_id, text=self.text)

        canvas.tag_raise(self.progress_id)
        canvas.tag_raise(self.text_id)
        canvas.tag_raise(self.outline_id)

    def set_text(self, canvas: tk.Canvas, rect: Rect, text: str):
        self.text = text
        self.draw(canvas, rect)

    def update(self, *, now: float, inside: bool, rect: Rect, canvas: tk.Canvas):
        if self._last_update == 0.0:
            self._last_update = now

        dt = max(0.0, now - self._last_update)
        self._last_update = now

        if inside:
            self._inside = True
            self.progress += 1.0 if self.fill_duration_s <= 0 else dt / self.fill_duration_s
            if self.progress >= 1.0:
                if self.on_trigger:
                    self.on_trigger()
                self.progress = 0.0
        else:
            if self._inside:
                self._inside = False
                self._last_exit = now
            if self._last_exit > 0.0 and (now - self._last_exit) >= self.grace_duration_s:
                self.progress = 0.0
                self._last_exit = 0.0

        self.draw(canvas, rect)


class TtsKeyboardPublisher(Publisher):
    def __init__(self, root_window):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root_window = root_window
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None

        self.tts = TTS()
        self.text_value = ""

        self.cursor_id: Optional[int] = None
        self._abs_rects: dict[str, Rect] = {}

        self._loop_after_id: Optional[str] = None
        self._loop_interval_ms = 33

        self.targets: list[Target] = []
        self.text_target_key = "text_target"
        self.logger.info("initialized")

    def start(self):
        self.window = tk.Toplevel(self.root_window)
        self.window.title("TTS Keyboard")
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)

        screen_w = self.window.winfo_screenwidth()
        x = screen_w - WINDOW_WIDTH
        y = 0
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.window, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        self._build_targets()
        self._start_loop()
        self.logger.info("started")

    def stop(self):
        self._stop_loop()
        try:
            if self.window is not None and self.window.winfo_exists():
                self.root.after(0, self.window.destroy)
        except tk.TclError:
            self.logger.warning("Tkinter window was already closed.")

        self.window = None
        self.canvas = None
        self.cursor_id = None
        self._abs_rects.clear()
        self.logger.info("stopped")

    def _has_focus(self) -> bool:
        return self.window is not None and self.window.focus_displayof() == self.window

    def _start_loop(self):
        self._stop_loop()
        self._loop_after_id = self.root_window.after(
            self._loop_interval_ms, self._loop)

    def _stop_loop(self):
        if self._loop_after_id is not None:
            try:
                self.root_window.after_cancel(self._loop_after_id)
            except Exception:
                pass
            self._loop_after_id = None

    def _loop(self):
        self._loop_after_id = None
        if self.canvas is None:
            return

        now = time.monotonic()
        if not self._has_focus():
            if self.cursor_id is not None:
                self.canvas.delete(self.cursor_id)
                self.cursor_id = None
            for t in self.targets:
                rect = self._abs_rects.get(t.key)
                if rect is not None:
                    t.update(now=now, inside=False,
                             rect=rect, canvas=self.canvas)

        self._start_loop()

    def _build_targets(self):
        self.targets = []

        def refresh_text():
            if self.canvas is None:
                return
            rect = self._abs_rects.get(self.text_target_key)
            if rect is None:
                return
            for t in self.targets:
                if t.key == self.text_target_key:
                    shown = self.text_value if self.text_value else ""
                    t.set_text(self.canvas, rect, shown)
                    return

        def speak_text():
            if self.text_value.strip():
                self.tts.speak(self.text_value)

        def add_char(c: str):
            self.text_value += c
            refresh_text()

        def delete_char():
            self.text_value = self.text_value[:-1] if self.text_value else ""
            refresh_text()

        def delete_word():
            s = self.text_value.rstrip(" ")
            if not s:
                self.text_value = ""
            else:
                head = s.rsplit(" ", 1)[0] if " " in s else ""
                self.text_value = (
                    head + (" " if head else "")) if head else ""
            refresh_text()

        def clear_all():
            self.text_value = ""
            refresh_text()

        # Top bar: text target + 3 buttons (no gap math)
        self.targets.append(
            Target(
                key=self.text_target_key,
                rel_rect=(0.00, 0.00, 0.70, 0.20),
                text="",
                on_trigger=speak_text,
                fill_duration_s=1.2,
                grace_duration_s=0.8,
                text_fill=TEXT_TARGET_FILL,
                font=TEXT_FONT,
                text_anchor="w",
            )
        )
        self.targets.append(Target(key="del_char", rel_rect=(
            0.70, 0.00, 0.80, 0.20), text="⌫", on_trigger=delete_char, font=TEXT_FONT))
        self.targets.append(Target(key="del_word", rel_rect=(
            0.80, 0.00, 0.90, 0.20), text="⌫W", on_trigger=delete_word, font=TEXT_FONT))
        self.targets.append(Target(key="del_all", rel_rect=(
            0.90, 0.00, 1.00, 0.20), text="CLR", on_trigger=clear_all, font=TEXT_FONT))

        # Keyboard rows (simple fixed relative boxes)
        def add_row(chars: str, x1: float, x2: float, y1: float, y2: float):
            n = len(chars)
            for i, ch in enumerate(chars):
                kx1 = x1 + (x2 - x1) * (i / n)
                kx2 = x1 + (x2 - x1) * ((i + 1) / n)
                self.targets.append(Target(key=f"key_{ch}", rel_rect=(
                    kx1, y1, kx2, y2), text=ch, on_trigger=(lambda c=ch: add_char(c))))

        add_row("qwertyuiop", 0.00, 1.00, 0.20, 0.40)
        add_row("asdfghjkl",  0.05, 0.95, 0.40, 0.60)
        add_row("zxcvbnm,.",   0.10, 1.00, 0.60, 0.80)

        self.targets.append(Target(key="space", rel_rect=(0.15, 0.80, 0.85, 1.00), text="␣",
                            on_trigger=lambda: add_char(" "), font=("TkDefaultFont", 22, "bold")))

    def _on_resize(self, _evt=None):
        if self.canvas is None:
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        self._abs_rects.clear()
        for t in self.targets:
            rect = t.layout(w, h)
            self._abs_rects[t.key] = rect
            t.draw(self.canvas, rect)

    def push(self, vector: Vector):
        if self.canvas is None or not self._has_focus():
            return

        now = time.monotonic()

        x_screen, y_screen = vector
        cx = x_screen - self.canvas.winfo_rootx()
        cy = y_screen - self.canvas.winfo_rooty()

        if not (0 <= cx <= self.canvas.winfo_width() and 0 <= cy <= self.canvas.winfo_height()):
            if self.cursor_id is not None:
                self.canvas.delete(self.cursor_id)
                self.cursor_id = None
            for t in self.targets:
                rect = self._abs_rects.get(t.key)
                if rect is not None:
                    t.update(now=now, inside=False,
                             rect=rect, canvas=self.canvas)
            return

        for t in self.targets:
            rect = self._abs_rects.get(t.key)
            if rect is None:
                continue
            t.update(now=now, inside=Target.contains(
                cx, cy, rect), rect=rect, canvas=self.canvas)

        if self.cursor_id is not None:
            self.canvas.delete(self.cursor_id)
        r = CURSOR_RADIUS
        self.cursor_id = self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r, fill=CURSOR_FILL, outline="")
        self.logger.debug(f"pushed vector: {vector}")
