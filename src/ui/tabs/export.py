from tkinter import *
from tkinter.ttk import *

import config


class ExportTab(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.export_path = StringVar(self, config.export_path)
        self.__init_widgets()

    def __init_widgets(self):
        path_container = Frame(self)
        Label(path_container, text="Export Path:").pack(anchor="w")
        self.__entry_path = Entry(
            path_container, width=67, textvariable=self.export_path
        )
        self.__entry_path.pack(side=LEFT)
        self.__btn_browse = Button(path_container, text="Browse", command=None)
        self.__btn_browse.pack(side=LEFT)
        path_container.pack(pady=(3, 0))
