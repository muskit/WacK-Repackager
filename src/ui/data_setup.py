from random import randint
from enum import Enum

from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk

import config


class TaskState(Enum):
    InProgress = 0
    Complete = 1
    Alert = 2
    Error = 3


class ProgressIcon(Frame):
    SIZE = 20

    image = {
        "progress": [
            Image.open("../assets/indeterminate_spinner.png")
            .convert("RGBA")
            .rotate(360 * (-i / 12))
            .resize((20, 20))
            for i in range(12)
        ],
        "complete": Image.open("../assets/task_complete.png")
        .convert("RGBA")
        .resize((20, 20)),
        "alert": Image.open("../assets/task_alert.png")
        .convert("RGBA")
        .resize((20, 20)),
        "error": Image.open("../assets/task_error.png")
        .convert("RGBA")
        .resize((20, 20)),
    }

    def __init__(self, master, init_status=TaskState.InProgress):
        super().__init__(master, height=ProgressIcon.SIZE, width=ProgressIcon.SIZE)
        self.mode = init_status
        self.label = Label(self)
        self.label.pack()
        self.loop()

    def loop(self, progress_counter=0):
        match self.mode:
            case TaskState.InProgress:
                self.image = ImageTk.PhotoImage(
                    ProgressIcon.image["progress"][progress_counter]
                )
            case TaskState.Complete:
                self.image = ImageTk.PhotoImage(ProgressIcon.image["complete"])
            case TaskState.Alert:
                self.image = ImageTk.PhotoImage(ProgressIcon.image["alert"])
            case TaskState.Error:
                self.image = ImageTk.PhotoImage(ProgressIcon.image["error"])

        self.label.configure(image=self.image)
        self.after(100, lambda: self.loop((progress_counter + 1) % 12))


class SetupProgress(Frame):
    def __init__(self, master, name: str = None, task=None):
        super().__init__(master)
        self.pack(fill="x")
        self.__init_widgets(name)

    def __init_widgets(self, name):
        Label(self, text=name).pack(side="left")

        ProgressIcon(self, init_status=TaskState(randint(0, 3))).pack(side="right")

        pb = Progressbar(
            self, mode="indeterminate", orient=HORIZONTAL, maximum=90, length=200
        )
        pb.pack(side="right", padx=(60, 12))
        pb.start(15)


class DataSetupWindow(Toplevel):
    def __init__(self, master, init_mode=False):
        super().__init__(master=master)

        self.title("Data Setup")
        self.geometry("500x250")
        self.resizable(False, False)

        self.str_path = StringVar(self, config.working_path)
        self.str_path.trace_add("write", self.__action_path_change)

        self.__init_widgets()

    def __init_widgets(self):
        # Path Field
        path_container = Frame(self)
        Label(path_container, text="Working Folder Path:").pack(anchor="w")
        self.entry_path = Entry(path_container, width=67, textvariable=self.str_path)
        self.entry_path.pack(side=LEFT)
        Button(path_container, text="Browse", command=None).pack(side=LEFT)
        path_container.pack(pady=(3, 0))

        # Progress
        progress_container = Frame(self)
        progress_container.pack(expand=True)
        SetupProgress(progress_container, "Metadata").pack()
        SetupProgress(progress_container, "Charts").pack()
        SetupProgress(progress_container, "Audio").pack()
        SetupProgress(progress_container, "Jackets").pack()
        SetupProgress(progress_container, "Videos").pack()

    def __action_path_change(self):
        pass
