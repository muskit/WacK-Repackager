import os
from configparser import ConfigParser

CONFIG_PATH = "./config.ini"

cfg_file_loaded: bool = None
"""If the config has been loaded or not.

None: config file has not attempted to load
False: could not load config file  
True: config file loaded successfully"""

working_path: str = os.path.abspath("./data")
export_path: str = os.path.abspath("./out")


def load():
    """Load config file and initialize variables."""
    global cfg_file_loaded
    cfp = ConfigParser()
    if len(cfp.read(CONFIG_PATH)) == 0:
        cfg_file_loaded = False  # config file missing, unreadable, or bad format
        return

    global working_path, export_path

    working_path = cfp.get("paths", "working_path", fallback=working_path)
    export_path = cfp.get("paths", "export_path", fallback=export_path)

    cfg_file_loaded = True


def save():
    """Save config file."""
    cfp = ConfigParser()

    global working_path

    ## Paths
    cfp.add_section("paths")
    cfp["paths"]["working_path"] = working_path
    cfp["paths"]["export_path"] = export_path

    cfp.set("paths", "working_path", working_path)
    cfp.set("paths", "export_path", export_path)

    print("Saving config file to", os.path.abspath(CONFIG_PATH))
    with open(CONFIG_PATH, "w") as f:
        cfp.write(f)
    print("Saved successfully!")
