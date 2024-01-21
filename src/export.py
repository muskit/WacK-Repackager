import os
import shutil
from pathlib import Path

from util import file_exists

import config
from data.database import *
from data.metadata import *
from ui.tabs.export_tab import ExportTab


def meta_mer(song: SongMetadata) -> str:
    """Contents of meta.mer based on song metadata."""
    ret = (
        f"#TITLE {song.name}\n"
        f"#RUBI {song.rubi}\n"
        f"#ARTIST {song.artist}\n"
        f"#GENRE {category_index[song.genre_id]}\n"
        f"#BPM {song.tempo}\n"
        f"#JACKET_FILE_PATH jacket.png\n"
    )
    if song.copyright != None:
        ret += f"#COPYRIGHT {song.copyright}\n"

    return ret


def diff_mer(mer: str, diff: Difficulty, audio_ext: str) -> str:
    """Returns a chart mer with WacK-specific meta tags."""

    ## keep mer line if not tag; otherwise, contains whitelisted tag
    whitelisted_tag_contains = ["OFFSET", "BODY"]

    ret = "\n".join(
        line
        for line in mer.splitlines()
        if any(
            not line.startswith("#") or tag in line for tag in whitelisted_tag_contains
        )
    )

    pre = (
        f"#LEVEL {diff.diffLevel}\n"
        f"#MUSIC_FILE_PATH {diff.audio_id}.{audio_ext}\n"
        f"#CLEAR_THRESHOLD {diff.clearRequirement}\n"
        f"#AUTHOR {diff.designer}\n"
        f"#PREVIEW_TIME {diff.audio_preview_time}\n"
        f"#PREVIEW_LENGTH {diff.audio_preview_length}\n"
    )

    if diff.video != None:
        pre += f"#MOVIE_FILE_PATH {os.path.basename(diff.video)}\n"

    return pre + ret


def export_song(song: SongMetadata):
    """Export a song to the export path."""
    from data.database import audio_file

    out = config.export_path
    if ExportTab.instance.option_game_subfolders.get():
        out = os.path.join(out, version_to_game[song.version])

    audio_ext = (
        ExportTab.instance.combobox_audio_conv_target.get()
        if ExportTab.instance.option_convert_audio.get()
        else "wav"
    )

    # create song folder
    song_path = os.path.join(out, f"{song.artist} - {song.name}")
    if not os.path.exists(song_path):
        Path(song_path).mkdir(parents=True, exist_ok=True)

    # copy jacket
    jacket_path = os.path.join(song_path, "jacket.png")
    shutil.copy2(song.jacket, jacket_path)

    # create meta.mer
    meta = meta_mer(song)
    meta_path = os.path.join(song_path, "meta.mer")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(meta)

    # per-difficulty operations
    for i, diff in enumerate(song.difficulties):
        if diff == None:
            continue

        # copy/convert audio named after song id if file doesn't exist
        a_id = diff.audio_id
        if audio_ext == "wav":
            search_regex = f"{a_id}.wav$"
            if not file_exists(song_path, search_regex):
                src = audio_file[a_id]
                dest = os.path.join(song_path, f"{a_id}.wav")
                shutil.copy2(src, dest)
        else:
            search_regex = f"{a_id}.{audio_ext}$"
            if not file_exists(song_path, search_regex):
                # TODO: convert to target format
                pass

        # copy video file
        if diff.video != None:
            dest = os.path.join(song_path, os.path.basename(diff.video))
            if not os.path.exists(dest):
                print(diff.video)
                shutil.copy2(diff.video, dest)

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


def export_selection_task(progress):
    """Export all selected songs from UI."""
    total = len(ExportTab.instance.treeview.selection())
    progress.pbar_set(prog=0, maximum=total)

    for id in ExportTab.instance.treeview.selection():
        song = metadata[id]
        export_song(song)
        progress.pbar_set(step=1, maximum=total)

    progress.status_set(TaskState.Complete)
