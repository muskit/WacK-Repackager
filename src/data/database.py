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
    metadata_path = f"{config.working_path}/metadata.json"
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

            # print(f'{id}: {name} - {artist}')
            if "S99" in id:
                # print('Skipping system song...')
                continue

            # mer difficulty-audio IDs
            mer_dir = f"{config.working_path}/MusicData/{id}"
            for root, _, files in os.walk(f"{mer_dir}"):
                for f in files:
                    diff_idx = int(re.search(r"\d\d.mer", f).group()[:2])

                    lines: list[str]
                    with open(f"{root}/{f}", "r") as chf:
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
            metadata[id] = SongMetadata(
                id=id,
                name=name,
                artist=artist,
                genre_id=genre,
                copyright=copyright,
                tempo=tempo,
                version=version,
                difficulties=difficulties,
            )
    except Exception as e:
        progress.enqueue_log(f"FATAL: Error occurred!")
        progress.enqueue_status(TaskState.Error)
        raise e

    progress.enqueue_progress_bar(prog=100)
    progress.enqueue_status(TaskState.Complete)
    progress.enqueue_log(f"Found {len(metadata)} songs.")


def __init_audio_index(progress: TaskProgress):
    csv_path = "./awb.csv"
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
    audio_dir = f"{config.working_path}/MER_BGM"
    print(f"Finding audio in {audio_dir}...")

    audio_file.clear()
    for k, v in audio_index.items():
        if v is None:
            progress.enqueue_log(f"WARNING: audio ID {k} has no cue index!!")
            continue
        f = f"{audio_dir}/{v[0]}/{v[1]}.wav"
        if os.path.exists(f):
            audio_file[k] = f
            progress.enqueue_progress_bar(prog=len(audio_file))
        else:
            progress.enqueue_log(f"WARNING: Could not find audio for {k} ({f})!")
    progress.enqueue_log(f"Found {len(audio_file)}/{len(audio_index)} audio files.")


def init_audio(progress: TaskProgress):
    __init_audio_index(progress)
    __init_audio_paths(progress)

    if len(audio_file) < len(audio_index):
        progress.enqueue_status(TaskState.Alert)
    else:
        progress.enqueue_status(TaskState.Complete)

    progress.enqueue_progress_bar(prog=len(audio_file))


# TODO
def init_jackets_task(progress: TaskProgress):
    jackets_dir = f"{config.working_path}/jackets"
    progress.enqueue_progress_bar(prog=0, maximum=len(metadata))

    jacket_file.clear()
    for _, _, files in os.walk(jackets_dir):
        for f in files:
            m = re.search(r"S\d\d-\d\d\d", f)
            if m is None:
                continue
            jacket_file[m.group()] = f
            progress.enqueue_progress_bar(prog=len(jacket_file))

    if len(jacket_file) < len(metadata):
        progress.enqueue_status(
            TaskState.Alert if len(jacket_file) < len(metadata) else TaskState.Complete
        )
        progress.enqueue_log(f"Found {len(jacket_file)}/{len(metadata)} jacket files.")


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
