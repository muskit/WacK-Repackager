import os
from queue import Empty, Queue
import shutil
from pathlib import Path

import ffmpeg

from util import *

import config
from data.database import *
from data.metadata import *


def meta_mer(song: SongMetadata) -> str:
    """Contents of meta.mer based on song metadata."""
    ret = (
        f"#TITLE {song.name}\n"
        f"#RUBI_TITLE {song.rubi}\n"
        f"#ARTIST {song.artist}\n"
        f"#GENRE {category_index[song.genre_id]}\n"
        f"#BPM {song.tempo}\n"
    )
    if song.copyright != None:
        ret += f"#COPYRIGHT {song.copyright}\n"

    return ret


def diff_mer(mer: str, diff: Difficulty, audio_ext: str) -> str:
    """Returns a chart mer with WacK-specific meta tags."""

    pre = (
        f"#--- BEGIN WACK TAGS ---\n"
        f"#LEVEL {diff.diffLevel}\n"
        f"#AUDIO {diff.audio_id}.{audio_ext}\n"
        f"#CLEAR_THRESHOLD {diff.clearRequirement}\n"
        f"#AUTHOR {diff.designer}\n"
        f"#PREVIEW_TIME {diff.audio_preview_time}\n"
        f"#PREVIEW_LENGTH {diff.audio_preview_length}\n"
    )

    if diff.video != None:
        pre += f"#MOVIE {os.path.basename(diff.video)}\n"

    return pre + "#--- END WACK TAGS ---\n" + mer


def export_song(song: SongMetadata):
    """Export a song to configured export path."""
    from data.database import audio_file
    from ui.tabs.export_tab import ExportTab

    alerts = []

    out = config.export_path
    if ExportTab.instance.option_game_subfolders.get():
        out = os.path.join(out, version_to_game[song.version])

    # desired audio extension from UI
    audio_ext = (
        ExportTab.instance.combobox_audio_conv_target.get()
        if ExportTab.instance.option_convert_audio.get()
        else "wav"
    )

    # create song folder
    song_path = os.path.join(out, sanitize(f"{song.artist} - {song.name}"))
    if not os.path.exists(song_path):
        Path(song_path).mkdir(parents=True, exist_ok=True)

    # create meta.mer
    meta = meta_mer(song)
    meta_path = os.path.join(song_path, "meta.mer")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(meta)

    # copy jacket
    src_jacket = os.path.join(song_path, "jacket.png")
    shutil.copy2(song.jacket, src_jacket)
    if ExportTab.instance.option_delete_originals.get():
        os.remove(src_jacket)

    # per-difficulty operations
    for i, diff in enumerate(song.difficulties):
        if diff == None:
            continue

        # copy/convert audio named after song id if file doesn't exist
        try:
            a_id = diff.audio_id
            src = audio_file[a_id]
            dest_regex = f"{a_id}.{audio_ext}$"
            if not file_exists(song_path, dest_regex):
                if audio_ext == "wav":
                    dest = os.path.join(song_path, f"{a_id}.wav")
                    shutil.copy2(src, dest)
                    if ExportTab.instance.option_delete_originals.get():
                        os.remove(src)
                else:
                    dest = os.path.join(song_path, f"{a_id}.{audio_ext}")
                    if audio_ext == "mp3":
                        print("Converting {a_id} to MP3...")
                        ffmpeg.input(src).output(
                            dest, audio_bitrate="320k", loglevel="warning"
                        ).run()
                    else:
                        ffmpeg.input(src).output(
                            dest, audio_bitrate="192k", loglevel="warning"
                        ).run()

                    if ExportTab.instance.option_delete_originals.get():
                        os.remove(src)
        except KeyError:
            alerts.append(f"Audio file not found for {DifficultyName(i).name}")

        # copy video file
        if diff.video != None and not ExportTab.instance.option_exclude_videos.get():
            dest = os.path.join(song_path, os.path.basename(diff.video))
            if not os.path.exists(dest):
                shutil.copy2(diff.video, dest)
                if ExportTab.instance.option_delete_originals.get():
                    os.remove(diff.video)

        # copy chart file with WacK-specific meta tags
        src = os.path.join(
            config.working_path, "MusicData", song.id, f"{song.id}_0{i}.mer"
        )
        dest = os.path.join(song_path, f"{i}.mer")

        with open(src, "r", encoding="utf-8") as f:
            mer = f.read()

        out = diff_mer(mer, diff, audio_ext)

        with open(dest, "w", encoding="utf-8") as f:
            f.write(out)

        # if ExportTab.instance.option_delete_originals.get():
        #     os.remove(src)

    return alerts
