import os
import sys
import tkinter as tk
from tkinter import ttk

import config
from guis.tkinter.hyperlink import Hyperlink


def _get_notes_file_path() -> str:
    base_dir = (
        config.WINDOWS_CONFIG_DIR
        if sys.platform.startswith("win")
        else config.LINUX_CONFIG_DIR
    )
    filename = f"release_notes_shown_{config.APP_VERSION}"
    return os.path.join(base_dir, filename)


def show_release_notes_if_needed(parent: tk.Misc) -> None:
    notes_file = _get_notes_file_path()

    if os.path.exists(notes_file):
        return

    os.makedirs(os.path.dirname(notes_file), exist_ok=True)

    dialog = tk.Toplevel(parent)
    dialog.title(f"Release notes ({config.APP_VERSION})")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)

    try:
        dialog.attributes("-topmost", True)
    except Exception:
        pass

    container = ttk.Frame(dialog, padding=16)
    container.pack(fill="both", expand=True)

    title = ttk.Label(container, text=f"Release notes ({config.APP_VERSION})", font=("TkDefaultFont", 12, "bold"))
    title.pack(anchor="w")

    notes = getattr(config, "APP_RELEASE_NOTES", "").strip() or f"You are running version {config.APP_VERSION}."
    notes_label = ttk.Label(container, text=notes, justify="left", wraplength=520)
    notes_label.pack(anchor="w", pady=(10, 16))

    links = ttk.Frame(container)
    links.pack(fill="x", pady=(0, 12))
    links.grid_columnconfigure(0, weight=0)
    links.grid_columnconfigure(1, weight=1)

    ttk.Label(links, text="Website:").grid(row=0, column=0, sticky="w", padx=3, pady=3)
    Hyperlink(links, url=config.APP_LINK_WEBSITE).grid(row=0, column=1, sticky="w", padx=3, pady=3)
    ttk.Label(links, text="Code:").grid(row=1, column=0, sticky="w", padx=3, pady=3)
    Hyperlink(links, url=config.APP_LINK_CODE).grid(row=1, column=1, sticky="w", padx=3, pady=3)

    btns = ttk.Frame(container)
    btns.pack(fill="x")

    def close():
        try:
            with open(notes_file, "w", encoding="utf-8") as f:
                f.write("shown\n")
        except Exception:
            pass
        try:
            dialog.grab_release()
        except Exception:
            pass
        dialog.destroy()

    ok = ttk.Button(btns, text="OK", command=close)
    ok.pack(side="right")

    dialog.protocol("WM_DELETE_WINDOW", close)

    dialog.update_idletasks()
    try:
        x = parent.winfo_rootx() + (parent.winfo_width() - dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    except Exception:
        pass

    dialog.wait_window()
