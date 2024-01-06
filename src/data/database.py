import csv
import os
import re
import json
from typing import Callable

import config
from ui.data_setup import TaskProgress, TaskState
from util import awb_index, song_id_from_int
from .metadata import Difficulty, SongMetadata

## NOTE: ID KEYS ARE HYPHENATED
## S03-014, not S03_014
metadata: dict[str, SongMetadata] = dict()
"""ID to SongMetadata"""

audio_index: dict[str, tuple[str, int]] = dict()
"""ID to AWB file and audio index"""

audio_file: dict[str, str] = dict()
"""ID to audio filename"""

jacket_file: dict[str, str] = dict()
"""ID to jacket filename"""

## MISSING CONTENT
missing_audio: list[str] = list()
"""List of songs missing audio"""

missing_jackets: list[str] = list()
"""List of songs missing jacket"""


# def init():
#     await _init_songs()
#     await _init_audio_index()
#     await _init_audio_paths()
#     await _init_jacket_paths()

#     print(f"{len(metadata)} songs' metadata found")
#     print(f"{len(jacket_file)} jackets found")
#     print(f"{len(audio_file)} audio files found")
#     print()

#     _populate_missing()
#     # print(audio_file)


def init_songs(progress: TaskProgress):
    jackets_dir = os.path.join(config.working_path, "jackets")
    metadata_path = os.path.join(config.working_path, "metadata.json")
    print(f"Initializing charts metadata from {metadata_path}...")

    metadata.clear()
    md_json: list
    try:
        with open(metadata_path, "r", encoding="utf_8") as read_file:
            md_json = json.load(read_file)["Exports"][0]["Table"]["Data"]

        for elem in md_json:  # songs
            id: str = None
            genre: int = None
            name: str = None
            artist: str = None
            copyright: str = None
            tempo: str = None
            version: int = None
            audio_preview: str = None
            audio_preview_len: str = None
            background_video: list[str] = [None, None, None, None]
            levels: list[str] = [None, None, None, None]
            level_audio: list[str] = [None, None, None, None]  # from .mer
            level_designer: list[str] = [None, None, None, None]
            level_clear_requirements: list[str] = [None, None, None, None]
            jacket_path: str = None

            # MusicParameterTable JSON parsing
            for key in elem["Value"]:  # properties of song
                if key["Name"] == "AssetDirectory":
                    id = key["Value"]
                # SongInfo
                elif key["Name"] == "ScoreGenre":
                    genre = int(key["Value"])
                elif key["Name"] == "MusicMessage":
                    name = key["Value"]
                elif key["Name"] == "ArtistMessage":
                    artist = key["Value"]
                elif key["Name"] == "Bpm":
                    tempo = key["Value"]
                elif key["Name"] == "CopyrightMessage" and key["Value"] not in [
                    "",
                    "-",
                    None,
                ]:
                    copyright = key["Value"]
                elif key["Name"] == "VersionNo":
                    version = key["Value"]
                elif key["Name"] == "JacketAssetName":
                    jacket_path = key["Value"]
                # ChartInfo Levels; "+0" = no chart
                elif key["Name"] == "DifficultyNormalLv":
                    levels[0] = key["Value"]
                elif key["Name"] == "DifficultyHardLv":
                    levels[1] = key["Value"]
                elif key["Name"] == "DifficultyExtremeLv":
                    levels[2] = key["Value"]
                elif key["Name"] == "DifficultyInfernoLv":
                    levels[3] = key["Value"]
                # Audio Previews
                elif key["Name"] == "PreviewBeginTime":
                    audio_preview = key["Value"]
                elif key["Name"] == "PreviewSeconds":
                    audio_preview_len = key["Value"]
                # Clear Requirements
                elif key["Name"] == "ClearNormaRateNormal":
                    level_clear_requirements[0] = key["Value"]
                elif key["Name"] == "ClearNormaRateHard":
                    level_clear_requirements[1] = key["Value"]
                elif key["Name"] == "ClearNormaRateExpert":
                    level_clear_requirements[2] = key["Value"]
                elif key["Name"] == "ClearNormaRateInferno":
                    level_clear_requirements[3] = key["Value"]
                # ChartInfo Designers
                elif key["Name"] == "NotesDesignerNormal":
                    level_designer[0] = key["Value"]
                elif key["Name"] == "NotesDesignerHard":
                    level_designer[1] = key["Value"]
                elif key["Name"] == "NotesDesignerExpert":
                    level_designer[2] = key["Value"]
                elif key["Name"] == "NotesDesignerInferno":
                    level_designer[3] = key["Value"]
                # Video Backgrounds
                elif key["Name"] == "MovieAssetName" and key["Value"] not in [
                    "",
                    "-",
                    None,
                ]:
                    background_video[0] = key["Value"]
                elif key["Name"] == "MovieAssetNameHard" and key["Value"] not in [
                    "",
                    "-",
                    None,
                ]:
                    background_video[1] = key["Value"]
                elif key["Name"] == "MovieAssetNameExpert" and key["Value"] not in [
                    "",
                    "-",
                    None,
                ]:
                    background_video[2] = key["Value"]
                elif key["Name"] == "MovieAssetNameInferno" and key["Value"] not in [
                    "",
                    "-",
                    None,
                ]:
                    background_video[3] = key["Value"]

            if "S99" in id:
                # print('Skipping system song...')
                continue

            # mer difficulty-audio IDs
            mer_dir = f"{config.working_path}/MusicData/{id}"
            for jacket_root, _, files in os.walk(f"{mer_dir}"):
                for f in files:
                    diff_idx = int(re.search(r"\d\d.mer", f).group()[:2])

                    lines: list[str]
                    with open(f"{jacket_root}/{f}", "r") as chf:
                        lines = chf.readlines()
                    a_id = None
                    offset = None
                    for l in lines:
                        if "MUSIC_FILE_PATH" in l:
                            a_id = re.search(r"S\d\d_\d\d\d", l.split()[1]).group()
                        elif "OFFSET" in l:
                            offset = l.split()[1]
                        if a_id and offset:
                            break

                    a_id = a_id.replace("_", "-")
                    level_audio[diff_idx] = (a_id, offset)

            # difficulty iteration -- level_audio has None for diffs w/o chart
            difficulties: list[Difficulty] = [None, None, None, None]
            for i, audio in enumerate(level_audio):
                if audio is None:
                    continue
                diff = Difficulty(
                    audio_id=audio[0],
                    audio_offset=audio[1],
                    audio_preview_time=audio_preview,
                    audio_preview_length=audio_preview_len,
                    video_id=background_video[i],
                    designer=level_designer[i],
                    clearRequirement=level_clear_requirements[i],
                    diffLevel=levels[i],
                )
                # use base video bg if video bg for this diff doesn't exist
                if (
                    i != 0
                    and background_video[i] is None
                    and background_video[0] is not None
                ):
                    diff.video_id = background_video[0]
                difficulties[i] = diff

            # jacket path to png
            jacket_root = os.path.join(jackets_dir, *jacket_path.split("/"))
            if os.path.isdir(jacket_root):
                for f in os.listdir(jacket_root):
                    if f.endswith(".png"):
                        jacket_path = os.path.join(jacket_root, f)
                        break
            else:
                jacket_path = f"{jacket_root}.png"

            if jacket_path is None or not os.path.exists(jacket_path):
                jacket_path = None
                progress.enqueue_log(f"WARNING: Could not find jacket for {id}!")

            metadata[id] = SongMetadata(
                id=id,
                name=name,
                artist=artist,
                genre_id=genre,
                copyright=copyright,
                tempo=tempo,
                version=version,
                difficulties=difficulties,
                jacket=jacket_path,
            )
    except Exception as e:
        progress.enqueue_log(f"FATAL: Error occurred!")
        progress.enqueue_status(TaskState.Error)
        raise e

    progress.enqueue_progress_bar(prog=100)
    progress.enqueue_status(TaskState.Complete)
    progress.enqueue_log(f"Found {len(metadata)} songs.")


def __init_audio_index(progress: TaskProgress):
    csv_path = os.path.abspath(os.path.join(os.path.curdir, "awb.csv"))
    print(f"Creating audio index from {csv_path}...")

    audio_index.clear()
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader)  # skip header

        for row in reader:
            v = awb_index(row[1])
            k = song_id_from_int(int(row[0]))

            audio_index[k] = v
    progress.enqueue_log(f"Found {len(audio_index)} audio indices.")
    progress.enqueue_progress_bar(prog=0, maximum=len(audio_index))


def __init_audio_paths(progress: TaskProgress):
    audio_dir = os.path.join(config.working_path, "MER_BGM")
    print(f"Finding audio in {audio_dir}...")

    # untouched files set to figure out which files weren't added
    # used for trying to fix holes in awb.csv
    untouched = set()

    # populate with full-path wav files in audio_dir
    for root, _, files in os.walk(audio_dir):
        for f in files:
            if "wav" in f:
                untouched.add(os.path.join(root, f))

    # populate audio_file with audio_index
    audio_file.clear()
    for k, v in audio_index.items():
        if v is None:
            progress.enqueue_log(f"WARNING: audio ID {k} has no cue index!!")
            if k in metadata:
                progress.enqueue_log(f"    {metadata[k].name} - {metadata[k].artist}")
            progress.enqueue_log(f"    This ID will have no sound!")
            continue

        f = os.path.join(audio_dir, v[0], f"{v[1]}.wav")
        f_eq = os.path.join(audio_dir, v[0], f"{v[1]+1}.wav")

        if os.path.exists(f):
            if audio_file.get(k) is not None:
                progress.enqueue_log(
                    f"WARNING: Duplicate audio ID {k}! Overwriting {audio_file[k]} with {f}"
                )

            audio_file[k] = f
            untouched.remove(f)
            untouched.remove(f_eq)
            progress.enqueue_progress_bar(prog=len(audio_file))
        else:
            progress.enqueue_log(f"WARNING: Could not find audio for {k} ({f})!")
    progress.enqueue_log(f"Found {len(audio_file)}/{len(audio_index)} audio files.")

    print(f"{len(untouched)} files weren't added:")
    for f in sorted(untouched):
        print(f"  {f}")


def init_audio(progress: TaskProgress):
    __init_audio_index(progress)
    __init_audio_paths(progress)

    if len(audio_file) < len(audio_index):
        progress.enqueue_status(TaskState.Alert)
    else:
        progress.enqueue_status(TaskState.Complete)

    progress.enqueue_progress_bar(prog=len(audio_file))


def jackets_progress_task(progress: TaskProgress):
    jackets_present = 0
    for k in metadata:
        if metadata[k].jacket is not None:
            jackets_present += 1

    progress.enqueue_status(
        TaskState.Alert if jackets_present < len(metadata) else TaskState.Complete
    )

    progress.enqueue_progress_bar(prog=jackets_present, maximum=len(metadata))
    progress.enqueue_log(f"Found {jackets_present}/{len(metadata)} jackets.")


# TODO
def videos_progress_task(progress: TaskProgress):
    progress.enqueue_log("TODO")


def _populate_missing():
    missing_audio.clear()
    missing_jackets.clear()

    # populate
    for k in metadata:
        if k not in audio_file:
            missing_audio.append(k)

        if k not in jacket_file:
            missing_jackets.append(k)

    # print
    print(f"Missing audio: {len(missing_audio)}")
    # for k in missing_audio:
    #     s = metadata[k]
    #     print(f"{s.id}: {s.name} - {s.artist}")
    # print()

    print(f"Missing jacket: {len(missing_jackets)}")
    # for k in missing_jackets:
    #     s = metadata[k]
    #     print(f"{s.id}: {s.name} - {s.artist}")
    # print()
