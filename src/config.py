from configparser import ConfigParser

CONFIG_PATH = "../config.ini"

config_loaded: bool = None
"""If the config has been loaded or not.

None: config file has not attempted to load
False: could not load config file  
True: config file loaded successfully"""

## PATHS
path_metadata: str = "../data/metadata.json"
"""Path to UAssetAPI-produced JSON file containing music metadata."""

path_charts: str = "../data/MusicData"
"""
Path to folder which contains charts.

Folder should only contain song ID-named folders, each of which contain .mer files.
This is how it's stored in WACCA's files (MusicData).
"""

path_audio: str = "../data/MER_BGM"
"""Path to folder which contains song audio."""

path_jackets: str = "../data/jackets"
"""Path to folder which contains song jackets."""

path_movies: str = "../data/movies"
"""Path to folder which contains movies (music video backgrounds)"""

## UI
ui_dark = False
"""Whether dark mode should be enabled for the whole UI or not."""


def load():
    """Load config file and initialize variables."""
    global config_loaded
    cfp = ConfigParser()
    if len(cfp.read(CONFIG_PATH)) == 0:
        config_loaded = False  # config file missing, unreadable, or bad format
        return

    global path_metadata, path_charts, path_audio, path_jackets, ui_dark

    # load paths
    path_metadata = cfp.get("paths", "file_metadata", fallback=path_metadata)
    path_charts = cfp.get("paths", "dir_charts", fallback=path_charts)
    path_audio = cfp.get("paths", "dir_audio", fallback=path_audio)
    path_jackets = cfp.get("paths", "dir_jackets", fallback=path_jackets)
    path_movies = cfp.get("paths", "dir_movies", fallback=path_movies)
    ui_dark = cfp.getboolean("ui", "dark_mode", fallback=ui_dark)

    config_loaded = True


def save():
    """Save config file."""
    cfp = ConfigParser()

    ## Paths
    cfp["paths"]["file_metadata"] = path_metadata
    cfp["paths"]["dir_charts"] = path_charts
    cfp["paths"]["dir_audio"] = path_audio
    cfp["paths"]["dir_jackets"] = path_jackets
    cfp["paths"]["dir_movies"] = path_movies

    ## UI
    cfp["ui"]["dark_mode"] = ui_dark

    with open(CONFIG_PATH, "w") as f:
        cfp.write(f)
