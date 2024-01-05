import os

import data.database as database
import config

from ui.ui_main import ui_main


def main():
    print("============== WacK Repackager ==============")
    config.load()
    ui_main()


if __name__ == "__main__":
    # Assume app is being run via a script at the project root.
    os.chdir("..")
    main()
