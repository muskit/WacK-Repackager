import os
import shutil
from pathlib import Path

from util import file_exists

import config
from data.database import *
from data.metadata import *
from ui.tabs.export import ExportTab


def meta_mer(song: SongMetadata) -> str:
    """Contents of meta.mer based on song metadata."""
    return (
        f"#TITLE {song.name}\n"
        f"#RUBI {song.rubi}\n"
        f"#ARTIST {song.artist}\n"
        f"#COPYRIGHT {song.copyright}\n"
        f"#GENRE {category_index[song.genre_id]}\n"
        f"#BPM {song.tempo}\n"
        f"#JACKET_FILE_PATH jacket.png\n"
    )


def diff_mer(mer: str, diff: Difficulty) -> str:
    """Returns a chart mer with WacK-specific meta tags."""

    ## keep mer line if not tag; otherwise, contains whitelisted tag
    whitelisted_tags = ["OFFSET", "BODY"]

    ret = "\n".join(
        line
        for line in mer.splitlines()
        if not any(not line.startswith("#") or tag in line for tag in whitelisted_tags)
    )

    ## TODO: add tags


def export_song(song: SongMetadata):
    """Export a song to the export path."""
    from data.database import audio_file

    out = config.export_path

    if ExportTab.instance.option_game_subfolders.get():
        out = os.path.join(out, game_version[song.version])

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

    # TODO: copy/convert audio file

    # per-difficulty operations
    for i, diff in enumerate(song.difficulties):
        if diff == None:
            continue

        # copy/convert audio named after song id if it doesn't exist
        a_id = diff.audio_id
        search_regex = f"{a_id}.(wav|mp3)$"
        if not file_exists(song_path, search_regex):
            if ExportTab.instance.option_mp3_convert.get():
                # TODO: convert to mp3
                pass
            else:
                # copy audio file
                src = audio_file[a_id]
                dest = os.path.join(song_path, f"{a_id}.wav")
                shutil.copy2(src, dest)

        # copy chart file
        src = os.path.join(
            config.working_path, "MusicData", song.id, f"{song.id}_0{i}.mer"
        )
        dest = os.path.join(song_path, f"{i}.mer")
        # TODO: change approach to extracting lines, getting rid of unnecessary meta tags
        shutil.copy2(src, dest)

        # TODO: add chart-specific meta tags to dest file

        # TODO: copy video file


def export_selection_task(progress):
    """Export all selected songs from UI."""
    total = len(ExportTab.instance.treeview.selection())
    progress.pbar_set(prog=0, maximum=total)

    for id in ExportTab.instance.treeview.selection():
        song = metadata[id]
        export_song(song)
        progress.pbar_set(step=1, maximum=total)

    progress.status_set(TaskState.Complete)
