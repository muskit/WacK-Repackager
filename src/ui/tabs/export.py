from __future__ import annotations

from enum import IntEnum
import os

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *

import config


class ExportGroup(IntEnum):
    ALL = 1
    SELECTED = 2
    FILTERED = 3


class ExportTab(Frame):
    instance: ExportTab = None

    def __init__(self, master):
        ExportTab.instance = self
        super().__init__(master)
        self.export_path = StringVar(self, config.export_path)
        self.export_path.trace_add("write", self.__action_path_change)

        self.export_group = IntVar(self, 0)
        self.export_group.trace_add("write", self.__action_group_change)

        # bool options
        self.option_game_subfolders = BooleanVar(self)
        self.option_delete_originals = BooleanVar(self)

        self.__init_widgets()
        self.export_group.set(ExportGroup.ALL)

    def __init_widgets(self):
        ## RIGHT BIGGER SIDE ##
        export_container = Frame(self, relief="flat")
        export_container.pack(side=RIGHT, fill=BOTH, expand=True)

        export_top = Frame(export_container)
        export_top.pack(fill=BOTH, expand=True)

        # Table of songs to be exported
        tv_scr = Scrollbar(export_top, orient=VERTICAL)
        self.exports_table = Treeview(export_top, yscrollcommand=tv_scr.set)
        tv_scr.configure(command=self.exports_table.yview)
        tv_scr.pack(fill=Y, side=RIGHT)
        self.exports_table.pack(fill=BOTH, expand=True, side=LEFT)

        # Export path and button
        export_btm = Frame(export_container)
        export_btm.pack(fill=X)
        path_container = LabelFrame(
            export_btm,
            text="Export Path",
        )
        self.__entry_path = Entry(
            path_container, width=67, textvariable=self.export_path
        )
        self.__entry_path.pack(side=LEFT, padx=(5, 0), pady=(0, 5))
        self.__btn_browse = Button(
            path_container, text="Browse", command=self.__action_dirpicker
        )
        self.__btn_browse.pack(side=LEFT, padx=(1, 5), pady=(0, 5))
        path_container.pack(pady=(3, 0), side=LEFT)

        self.__btn_export = Button(export_btm, text="Export", command=None)
        self.__btn_export.pack(side=RIGHT, anchor="s", pady=8)

        ## LEFT SMALLER SIDE ##
        options_container = Frame(self, relief="solid", width=250)
        options_container.pack_propagate(0)
        options_container.pack(side=LEFT, fill=Y)
        Label(options_container, text="Export Options", background="lightgray").pack(
            fill=X, padx=1, pady=1
        )

        # Export group options
        export_group_options = LabelFrame(options_container, text="Group to Export")
        export_group_options.pack(fill=X, padx=(5, 15), pady=(10, 20))
        Radiobutton(
            export_group_options,
            text="Export ALL Songs",
            variable=self.export_group,
            value=ExportGroup.ALL,
        ).pack(anchor="w", padx=5)
        Radiobutton(
            export_group_options,
            variable=self.export_group,
            text="Export Selected Songs",
            value=ExportGroup.SELECTED,
        ).pack(anchor="w", padx=5)
        Radiobutton(
            export_group_options,
            variable=self.export_group,
            text="Export Filtered Songs",
            value=ExportGroup.FILTERED,
        ).pack(anchor="w", padx=5)

        # Other options
        Checkbutton(
            options_container,
            text="Export to Subfolders by Game",
            variable=self.option_game_subfolders,
        ).pack(anchor="w", padx=5)

        Checkbutton(
            options_container,
            text="Delete Original Files",
            variable=self.option_delete_originals,
        ).pack(anchor="w", padx=5)

    def __action_path_change(self, *_):
        config.export_path = self.export_path.get()

    def __action_dirpicker(self):
        result = filedialog.askdirectory(initialdir=config.export_path)
        if result != "":
            self.export_path.set(result)

    def __action_group_change(self, *_):
        print(f"Export group set to {ExportGroup(self.export_group.get()).name}")
