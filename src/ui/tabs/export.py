from __future__ import annotations

from enum import IntEnum, StrEnum
import ffmpeg

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *

import config
import data.database as db
import data.metadata as md
from util import ffmpeg_on_path
from .listing import ListingTab


class ExportGroup(IntEnum):
    ALL = 1
    SELECTED = 2
    FILTERED = 3


class AudioConvertTarget(StrEnum):
    MP3 = "mp3"
    OGG = "ogg"


class ExportTab(Frame):
    instance: ExportTab = None

    def __init__(self, master):
        ExportTab.instance = self
        super().__init__(master)
        self.export_path = StringVar(self, config.export_path)
        self.export_path.trace_add("write", self.__action_path_change)

        self.export_group = IntVar(self, 0)
        self.export_group.trace_add("write", self.__refresh_exports_table)

        # bool options
        self.option_game_subfolders = BooleanVar(self)
        self.option_delete_originals = BooleanVar(self)
        self.option_convert_audio = BooleanVar(self)
        self.option_convert_audio.trace_add("write", self.__action_audio_conv_change)
        self.option_audio_target = StringVar(self, AudioConvertTarget.MP3)
        self.option_exclude_videos = BooleanVar(self)

        self.__init_widgets()

    def __init_widgets(self):
        ## RIGHT BIGGER SIDE ##
        export_container = Frame(self, relief="flat")
        export_container.pack(side=RIGHT, fill=BOTH, expand=True)

        export_top = Frame(export_container)
        export_top.pack(fill=BOTH, expand=True)

        # Table of songs to be exported
        tv_scr = Scrollbar(export_top, orient=VERTICAL)
        self.treeview = Treeview(
            export_top,
            yscrollcommand=tv_scr.set,
            columns=("id", "title", "artist", "game"),
        )
        tv_scr.configure(command=self.treeview.yview)
        tv_scr.pack(fill=Y, side=RIGHT)
        self.treeview.pack(fill=BOTH, expand=True, side=LEFT)

        self.treeview.column("#0", width=0, stretch=False)
        self.treeview.heading("id", text="ID", anchor=CENTER)
        self.treeview.column("id", width=75, stretch=False, anchor=CENTER)
        self.treeview.heading("title", text="Song Name", anchor=W)
        self.treeview.heading("artist", text="Artist", anchor=W)
        self.treeview.heading("game", text="Game", anchor=W)
        self.treeview.column("game", width=150, stretch=False)

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
        self.radio_exp_selected = Radiobutton(
            export_group_options,
            variable=self.export_group,
            text="Export Selected Songs",
            value=ExportGroup.SELECTED,
        )
        self.radio_exp_selected.pack(anchor="w", padx=5)
        self.radio_exp_filtered = Radiobutton(
            export_group_options,
            variable=self.export_group,
            text="Export Filtered Songs",
            value=ExportGroup.FILTERED,
        )
        self.radio_exp_filtered.pack(anchor="w", padx=5)

        # Other options
        audio_conv_options = LabelFrame(options_container, text="Audio Conversion")
        audio_conv_options.pack(fill=X, padx=(5, 15), pady=(10, 20))
        Checkbutton(
            audio_conv_options,
            text="Convert Audio from WAV"
            + ("\n(ffmpeg not found on PATH!)" if not ffmpeg_on_path() else ""),
            variable=self.option_convert_audio,
            state=DISABLED if not ffmpeg_on_path() else NORMAL,
        ).pack(anchor="w", padx=5)
        self.combobox_audio_conv_target = Combobox(
            audio_conv_options,
            state=DISABLED,
            values=[s.value for s in AudioConvertTarget],
            textvariable=self.option_audio_target,
        )
        self.combobox_audio_conv_target.pack()

        Checkbutton(
            options_container,
            text="Exclude Videos",
            variable=self.option_exclude_videos,
        ).pack(anchor="w", padx=5)

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

    def __action_audio_conv_change(self, *_):
        self.combobox_audio_conv_target.configure(
            state="readonly" if self.option_convert_audio.get() else DISABLED
        )

    def __refresh_exports_table(self, *_):
        self.treeview.delete(*self.treeview.get_children())

        match self.export_group.get():
            case ExportGroup.ALL:
                print("Adding ALL songs...")
                for song in db.metadata.values():
                    self.treeview.insert(
                        "",
                        "end",
                        id=song.id,
                        values=(
                            song.id,
                            song.name,
                            song.artist,
                            md.version_to_game[song.version],
                        ),
                    )
            case ExportGroup.SELECTED:
                print("Adding SELECTED songs...")
                for id in ListingTab.instance.treeview.selection():
                    song = db.metadata[id]
                    self.treeview.insert(
                        "",
                        "end",
                        id=song.id,
                        values=(
                            song.id,
                            song.name,
                            song.artist,
                            md.version_to_game[song.version],
                        ),
                    )
            case ExportGroup.FILTERED:
                print("Adding FILTERED songs...")
                for id in ListingTab.instance.treeview.get_children():
                    song = db.metadata[id]
                    self.treeview.insert(
                        "",
                        "end",
                        id=song.id,
                        values=(
                            song.id,
                            song.name,
                            song.artist,
                            md.version_to_game[song.version],
                        ),
                    )

    def refresh(self):
        if ListingTab.instance.filter_game.get() == "None":
            self.radio_exp_filtered.configure(state=DISABLED)
        else:
            self.radio_exp_filtered.configure(state=NORMAL)

        if len(ListingTab.instance.treeview.selection()) == 0:
            self.radio_exp_selected.configure(state=DISABLED)
            if self.export_group.get() in (0, ExportGroup.SELECTED):
                if ListingTab.instance.filter_game.get() == "None":
                    self.export_group.set(ExportGroup.ALL)
                else:
                    self.export_group.set(ExportGroup.FILTERED)
            elif ListingTab.instance.filter_game.get() != "None":
                self.export_group.set(ExportGroup.FILTERED)
        else:
            self.radio_exp_selected.configure(state=NORMAL)
            self.export_group.set(ExportGroup.SELECTED)

        self.__refresh_exports_table()
