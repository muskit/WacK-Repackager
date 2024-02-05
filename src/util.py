import os
import re
import shutil
import sys

from tkinter import Widget


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


VERSION = open(resource_path("version.txt")).read().strip()


def song_id_from_int(num: int):
    if num < 0:
        raise ValueError("cannot be negative")

    if num <= 999:
        return f"S00-{str(num).zfill(3)}"

    s = int(num / 1000)
    return f"S{str(s).zfill(2)}-{str(num - 1000*s).zfill(3)}"


def awb_index(id: str):
    tokens = id.split("_")
    if len(tokens) < 2:
        return None
    return (tokens[0], int(tokens[1]))


def ffmpeg_on_path() -> bool:
    """Check if ffmpeg is on the system path."""
    return shutil.which("ffmpeg") != None


def file_exists(path: str, regex: str) -> bool:
    """Check if a file exists in a directory based on regex."""
    for file in os.listdir(path):
        if re.match(regex, file, re.IGNORECASE):
            return True
    return False


def disable_children_widgets(widget: Widget):
    """Disable all nested children widgets."""
    for child in widget.winfo_children():
        if len(child.winfo_children()) > 0:
            disable_children_widgets(child)
        else:
            try:
                child.original_state = child.cget("state")
                child.configure(state="disable")
            except:
                pass


def enable_children_widgets(widget: Widget):
    """Re-enable all nested children widgets that were disabled using \"disable_children_widgets.\" """
    for child in widget.winfo_children():
        if len(child.winfo_children()) > 0:
            enable_children_widgets(child)
        else:
            try:
                child.configure(state=child.original_state)
            except:
                pass


def sanitize_song(folder_name: str):
    blacklist = ["\\", "/", ":", "*", "?", '"', "'", "<", ">", "|"]
    return "".join([x if x not in blacklist else "_" for x in folder_name]).strip()
