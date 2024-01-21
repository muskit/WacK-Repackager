import os
import re
import shutil


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
