import csv
import os
import re
import json

import config
from util import awb_index, song_id_from_int
from .metadata import Difficulty, SongMetadata

## NOTE: ID KEYS ARE HYPHENATED
## S03-014, not S03_014
metadata: dict[str, SongMetadata] = dict()
"""ID to SongMetadata"""

audio_index: dict[str, (str, int)] = dict()
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


def init():
    _init_songs()
    _init_audio_index()
    _init_audio_paths()
    _init_jacket_paths()
    print(f"{len(metadata)} songs' metadata found")
    print(f"{len(jacket_file)} jackets found")
    print(f"{len(audio_file)} audio files found")
    _populate_missing()
    # print(audio_file)


def _init_songs():
    print("Initializing charts metadata...")
    metadata.clear()
    md_json: list
    with open(config.path_metadata, "r", encoding="utf_8") as read_file:
        md_json = json.load(read_file)["Exports"][0]["Table"]["Data"]

    for elem in md_json:  # songs
        id: str = None
        genre: int = None
        name: str = None
        artist: str = None
        copyright: str = None
        tempo: str = None
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
        mer_dir = f"{config.path_charts}/{id}"
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

                level_audio[diff_idx] = (a_id, offset)
                print(level_audio[diff_idx])

        # difficulty iteration -- level_audio has None for diffs w/o chart
        difficulties: list[Difficulty] = [None, None, None, None]
        for i, audio in enumerate(level_audio):
            if audio is None:
                continue
            curd = Difficulty(
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
                curd.video_id = background_video[0]
            difficulties[i] = curd
        metadata[id] = SongMetadata(
            id=id,
            name=name,
            artist=artist,
            genre_id=genre,
            copyright=copyright,
            tempo=tempo,
            difficulties=difficulties,
        )


def _init_audio_index():
    with open("../awb.csv") as f:
        reader = csv.reader(f)
        next(reader)  # skip header

        for row in reader:
            v = awb_index(row[1])
            if v is None:
                continue
            k = song_id_from_int(int(row[0]))

            print(f"{k}: {v}")
            audio_index[k] = v


def _init_audio_paths():
    print(f"Finding audio in {config.path_audio}")
    for _, _, files in os.walk(config.path_audio):
        for f in files:
            m = re.search(r"S\d\d_\d\d\d", f)
            if m is None:
                continue

            _id = m.group()
            id = f"{_id[:3]}-{_id[4:]}"
            if id in audio_file:
                # lexicographically smaller file has proper audio
                audio_file[id] = min(audio_file[id], f)
            else:
                audio_file[id] = f


def _init_jacket_paths():
    print(f"Finding jackets in {config.path_jackets}")
    for _, _, files in os.walk(config.path_jackets):
        for f in files:
            m = re.search(r"S\d\d-\d\d\d", f)
            if m is None:
                continue
            jacket_file[m.group()] = f


def _populate_missing():
    for k in metadata:
        # check missing audio
        if k not in audio_file:
            missing_audio.append(k)
        # check missing jackets
        if k not in jacket_file:
            missing_jackets.append(k)

    # # print missing audio
    # print(f"Missing audio: {len(missing_audio)}")
    # for k in missing_audio:
    #     s = metadata[k]
    #     print(f"{s.id}: {s.name} - {s.artist}")
    # print()
    # # print missing jackets
    # print(f"Missing jacket: {len(missing_jackets)}")
    # for k in missing_jackets:
    #     s = metadata[k]
    #     print(f"{s.id}: {s.name} - {s.artist}")
    # print()
