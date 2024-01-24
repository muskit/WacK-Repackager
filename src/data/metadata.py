from dataclasses import dataclass, field
from enum import Enum
from math import floor

category_index = {
    -1: "Unknown",
    0: "Anime/Pop",
    1: "Vocaloid",
    2: "Touhou Project",
    3: "2.5D",
    4: "Variety",
    5: "Original",
    6: "HARDCORE TANO*C",
    7: "VTuber",
}


class DifficultyName(Enum):
    Normal = 0
    Hard = 1
    Expert = 2
    Inferno = 3


version_to_game = {
    1: "".join(map(chr, [87, 65, 67, 67, 65])),
    2: "".join(map(chr, [87, 65, 67, 67, 65, 32, 83])),
    3: "".join(map(chr, [87, 65, 67, 67, 65, 32, 76, 73, 76, 89])),
    4: "".join(map(chr, [87, 65, 67, 67, 65, 32, 76, 73, 76, 89, 32, 82])),
    5: "".join(map(chr, [87, 65, 67, 67, 65, 32, 82, 101, 118, 101, 114, 115, 101])),
}

game_to_version = {v: k for k, v in version_to_game.items()}


@dataclass
class Difficulty:
    audio_id: str
    audio_offset: str
    audio_preview_time: str
    audio_preview_length: str
    video: str | None
    designer: str
    clearRequirement: str
    diffLevel: str

    def diff_str(self):
        val = float(self.diffLevel)
        fl = floor(val)
        return f'{fl}{"+" if fl < val else ""}'


@dataclass
class SongMetadata:
    id: str
    """Format: Snn-nnn"""
    name: str
    artist: str
    rubi: str
    genre_id: int
    copyright: str
    tempo: str
    version: int
    difficulties: list[Difficulty | None] = field(default_factory=list)
    jacket: str = None
