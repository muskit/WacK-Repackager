from dataclasses import dataclass, field
from enum import Enum
from math import floor

category_index = {
	-1: 'Unknown',
	0: 'Anime/Pop',
	1: 'Vocaloid',
	2: 'Touhou Project',
	3: '2.5D',
	4: 'Variety',
	5: 'Original',
	6: 'HARDCORE TANO*C',
	7: 'VTuber'
}

class DifficultyName(Enum):
	Normal = 0
	Hard = 1
	Expert = 2
	Inferno = 3

@dataclass
class Difficulty:
	audio_id: str
	audio_offset: str
	audio_preview_time: str
	audio_preview_length: str
	video_id: str | None
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
	name: str
	artist: str
	genre_id: int
	copyright: str
	tempo: str
	difficulties: list[Difficulty | None] = field(default_factory=list)
