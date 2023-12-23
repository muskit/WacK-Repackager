from configparser import ConfigParser

CONFIG_PATH = "../config.ini"

config_loaded: bool = None
"""If the config has been loaded or not.

None: config file has not attempted to load
False: could not load config file  
True: config file loaded successfully"""

working_path: str = "../data"


def load():
    """Load config file and initialize variables."""
    global config_loaded
    cfp = ConfigParser()
    if len(cfp.read(CONFIG_PATH)) == 0:
        config_loaded = False  # config file missing, unreadable, or bad format
        return

    global working_path

    working_path = cfp.get("paths", "working_path", fallback=working_path)

    config_loaded = True


def save():
    """Save config file."""
    cfp = ConfigParser()

    global working_path

    ## Paths
    cfp["paths"]["working_path"] = working_path

    with open(CONFIG_PATH, "w") as f:
        cfp.write(f)
