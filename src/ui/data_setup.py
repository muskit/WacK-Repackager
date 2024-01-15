from __future__ import annotations
from datetime import datetime
from threading import Thread
from collections import deque
from queue import Queue, Empty
import traceback
from typing import Any, Callable
from random import randint
from enum import Enum
import os

from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from PIL import Image, ImageTk

import config
from data import database


class TaskState(Enum):
    InProgress = 0
    Complete = 1
    Alert = 2
    Error = 3


class ProgressIcon(Frame):
    image = {
        "progress": [
            Image.open("./assets/indeterminate_spinner.png")
            .convert("RGBA")
            .rotate(360 * (-i / 12))
            .resize((20, 20))
            for i in range(12)
        ],
        "complete": Image.open("./assets/task_complete.png")
        .convert("RGBA")
        .resize((20, 20)),
        "alert": Image.open("./assets/task_alert.png").convert("RGBA").resize((20, 20)),
        "error": Image.open("./assets/task_error.png").convert("RGBA").resize((20, 20)),
    }

    def __init__(self, master, init_status=TaskState.InProgress):
        super().__init__(master, height=20, width=20)
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


class TaskProgress(Frame):
    def __init__(
        self,
        master,
        name: str = None,
        task: Callable[[TaskProgress], None] = None,
        log: Callable[[str], None] = None,
    ):
        super().__init__(master)
        self.name = name
        self.task = task
        self.__log_func = log
        self.event_queue = Queue()

        self.pack(fill="x")
        self.__init_widgets()
        self.after(1, self.__event_queue_process)

    def __init_widgets(self):
        Label(self, text=self.name).pack(side="left")

        self.prg_icn = ProgressIcon(self)
        self.prg_icn.pack(side="right")

        self.p_bar_val = IntVar()
        self.p_bar = Progressbar(
            self,
            mode="indeterminate",
            orient=HORIZONTAL,
            maximum=90,
            length=250,
            variable=self.p_bar_val,
        )
        self.p_bar.pack(side="right", padx=(40, 12))
        self.p_bar.start(15)

    def __event_queue_process(self):
        try:
            while True:
                msg = self.event_queue.get_nowait()
                match msg[0]:
                    case "p_bar":
                        self.__set_progress(msg[1], msg[2], msg[3], msg[4])
                    case "state":
                        self.__set_status(msg[1])
                    case "log":
                        self.__log_func(f"[{self.name}] {msg[1]}")
        except Empty:
            pass

        self.after(1, self.__event_queue_process)

    def __set_progress(
        self, step: int = None, prog: int = None, maximum: int = None, stop_anim=False
    ):
        if maximum is not None:
            self.p_bar["max"] = maximum

        if step is None and prog is None:
            self.p_bar["mode"] = "indeterminate"
            self.p_bar.start(15) if not stop_anim else self.p_bar.stop()
        else:
            self.p_bar.stop()
            self.p_bar["mode"] = "determinate"

            if prog is not None:
                self.p_bar_val.set(prog)

            if step is not None:
                self.p_bar.step(step)

    def __set_status(self, status: TaskState = None):
        self.prg_icn.mode = status

    # ENQUEUE EVENTS FOR GUI UPDATE (__event_queue_process)
    def enqueue_status(self, status: TaskState):
        self.event_queue.put_nowait(("state", status))

    def enqueue_progress_bar(
        self, step: int = None, prog: int = None, maximum: int = None, stop_anim=False
    ):
        self.event_queue.put_nowait(("p_bar", step, prog, maximum, stop_anim))

    def enqueue_log(self, msg):
        # DataSetupWindow has logging queue
        self.__log_func(f"[{self.name}] {msg}")


class DataSetupWindow(Toplevel):
    def __init__(self, master, file_picker_init=False):
        super().__init__(master=master)

        self.title("Data Setup")
        self.geometry("550x500")
        self.resizable(False, False)

        self.str_path = StringVar(self, config.working_path)
        # self.str_path.trace_add("write", self.__action_path_change)
        self.protocol("WM_DELETE_WINDOW", self.__action_close)

        self.__tasks: deque[TaskProgress] = deque(maxlen=5)
        self.__cur_tasks_thread: Thread = None
        self.__working = False

        self.event_queue: Queue[tuple[str, Any]] = Queue()
        self.__init_widgets()
        self.reset_tasks()

    def __init_widgets(self):
        # Path Field
        path_container = Frame(self)
        Label(path_container, text="Working Folder Path:").pack(anchor="w")
        self.entry_path = Entry(path_container, width=67, textvariable=self.str_path)
        self.entry_path.pack(side=LEFT)
        Button(path_container, text="Browse", command=None).pack(side=LEFT)
        path_container.pack(pady=(3, 0))

        # Progress
        self.progress_container = Frame(self)
        self.progress_container.pack(expand=True, side="top", anchor="n", pady=10)

        self.__btn_rescan = Button(self, text="Rescan", command=self.reset_tasks)
        self.__btn_rescan.pack(pady=(0, 10))

        # Log window
        self.log_win = ScrolledText(self)
        self.log_win["state"] = "disabled"
        self.log_win.pack(padx=20, pady=(0, 20))
        self.after(10, self.__event_queue_process)

    def __event_queue_process(self):
        try:
            while True:
                msg = self.event_queue.get_nowait()
                match msg[0]:
                    case "working":
                        # msg[1] is bool
                        self.__working = msg[1]

                        if self.__working:
                            self.__btn_rescan["state"] = "disabled"
                        else:
                            self.__btn_rescan["state"] = "normal"
                    case "log":
                        # msg[1] is str
                        self.__log_insert(msg[1])
        except Empty:
            pass

        self.after(10, self.__event_queue_process)

    def __log_insert(self, msg: str):
        self.log_win["state"] = "normal"
        self.log_win.insert("end", f"{msg}\n")
        self.log_win["state"] = "disabled"
        self.log_win.see("end")

    def __action_path_change(self):
        pass

    def __action_close(self):
        if not self.__working:
            self.destroy()

    def log(self, msg: str):
        self.event_queue.put_nowait(("log", msg))

    def reset_tasks(self):
        while len(self.__tasks) > 0:
            self.__tasks.pop().destroy()

        if os.path.isdir(self.str_path.get()):
            self.str_path.set(os.path.abspath(self.str_path.get()))
            config.working_path = self.str_path.get()

        t_md = TaskProgress(
            self.progress_container,
            "Metadata",
            database.init_songs,
            self.log,
        )
        t_md.pack()
        self.__tasks.append(t_md)

        t_a = TaskProgress(
            self.progress_container, "Audio", database.init_audio, self.log
        )
        t_a.pack()
        self.__tasks.append(t_a)

        t_j = TaskProgress(
            self.progress_container, "Jackets", database.jackets_progress_task, self.log
        )
        t_j.pack()
        self.__tasks.append(t_j)

        self.start_tasks()

    def start_tasks(self):
        """Tasks thread starter"""

        if self.__cur_tasks_thread is not None:
            self.__cur_tasks_thread.join()
        self.__cur_tasks_thread = Thread(target=self.__tasks_thread)

        self.event_queue.put_nowait(("working", True))
        self.__cur_tasks_thread.start()

    def __tasks_thread(self):
        self.log(
            f"Beginning scan at {datetime.now().isoformat(sep=' ', timespec='seconds')}"
        )
        try:
            for t in self.__tasks:
                t.task(t)
        except:
            for t in self.__tasks:
                t.enqueue_progress_bar(stop_anim=True)
            self.log(f"ERROR:\n{traceback.format_exc()}\n\nAborting.")

        self.log("")
        print("Tasks thread finished")
        self.event_queue.put_nowait(("working", False))
