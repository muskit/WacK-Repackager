from __future__ import annotations

from enum import IntEnum

from ..util import *

from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont

from PIL import Image, ImageTk

from util import resource_path
import data.database as db
from data.metadata import *


class MetadataPanel(Frame):
    img_jacket_placeholder = Image.open(
        resource_path("assets/jacket-placeholder.png")
    ).resize((200, 200))

    def __init__(self, master):
        super().__init__(master, width=220, relief=GROOVE)
        self.pack_propagate(False)
        self.init_widgets()
        self.jackets: dict[str, ImageTk.PhotoImage] = {}

    def init_widgets(self):
        self.lbl_id = Label(self, text="Song ID", anchor=CENTER, background="lightgray")
        self.lbl_id.pack(fill=X, padx=(1, 2), pady=1)

        self.image = ImageTk.PhotoImage(self.img_jacket_placeholder)
        self.md_img = Label(self, image=self.image)
        self.md_img.pack(pady=10)

        f = tkFont.nametofont("TkDefaultFont").actual()
        self.lbl_name = Label(self, text="Song Name", anchor=CENTER)
        self.lbl_name.configure(font=(f["family"], 14, ""))
        self.lbl_name.pack(fill=X, padx=4)

        self.lbl_artist = Label(self, text="Artist", anchor=CENTER)
        self.lbl_artist.pack(fill=X, padx=4)

        # Spacer
        Frame(self, height=10).pack(fill="y")

        self.lbl_game = Label(self, text="Game Release", anchor=CENTER)
        self.lbl_game.pack(fill=X, padx=4)

        # Spacer
        Frame(self, height=10).pack(fill="y")

    def set_song(self, song: SongMetadata):
        self.lbl_id.configure(text=song.id)
        self.image = self.jackets[song.id]
        self.md_img.configure(image=self.image)
        self.lbl_name.configure(text=song.name)
        try_ellipsis(self.lbl_name)
        self.lbl_artist.configure(text=song.artist)
        try_ellipsis(self.lbl_artist)
        self.lbl_game.configure(text=version_to_game[song.version])


class ListingTab(Frame):
    instance: ListingTab = None

    class FilterType(IntEnum):
        NONE = 0
        TITLE = 1
        ARTIST = 2
        GENRE = 3
        GAME = 4

    def __init__(self, master):
        ListingTab.instance = self
        super().__init__(master)

        self.__table_cur_col_sort: str = None
        self.__table_rev_sort: bool = False
        self.filter_game = StringVar(self, "None")
        self.filter_game.trace_add("write", lambda *_: self.table_populate())
        self.__init_widgets()

    def __init_widgets(self):
        ## Left Half
        left_container = Frame(self)
        left_container.pack(fill=BOTH, expand=True, side=LEFT)
        # Table of songs in database
        table_container = Frame(left_container)
        table_container.pack(fill=BOTH, expand=True, side=TOP)
        self.treeview = Treeview(
            table_container, columns=("id", "title", "artist", "genre")
        )
        self.treeview.column("#0", width=0, stretch=False)
        self.treeview.pack(fill=BOTH, expand=True, side=LEFT)
        self.treeview.tag_configure("oddrow", background="#f0f0ff")
        self.treeview.bind("<<TreeviewSelect>>", self.__on_table_select)

        self.treeview.heading("id", text="ID", anchor=CENTER)
        self.treeview.column("id", width=75, stretch=False, anchor=CENTER)
        self.treeview.heading("title", text="Song Name", anchor=W)
        self.treeview.heading("artist", text="Artist", anchor=W)
        self.treeview.heading("genre", text="Genre", anchor=W)
        self.treeview.column("genre", width=150, stretch=False)

        self.treeview.bind("<Button-1>", self.__on_table_click)

        tv_scr = Scrollbar(
            table_container, orient=VERTICAL, command=self.treeview.yview
        )
        tv_scr.pack(fill=Y, side=RIGHT)
        self.treeview.configure(yscrollcommand=tv_scr.set)

        filter_container = Frame(left_container)
        filter_container.pack(fill=X, side=BOTTOM, pady=(2, 0), padx=2)
        Label(filter_container, text="Filter by game version:").pack(side=LEFT, padx=2)
        Combobox(
            filter_container,
            state="readonly",
            values=["None"] + list(game_to_version.keys()),
            textvariable=self.filter_game,
        ).pack(side=LEFT, pady=(2, 0), padx=2)
        f = tkFont.nametofont("TkDefaultFont").actual()
        self.lbl_selected = Label(
            filter_container,
            text="0/0 songs selected for export",
            font=(f["family"] + " Italic", f["size"], ""),
        )
        self.lbl_selected.pack(side=RIGHT, padx=2)

        ## Right Half
        right_container = Frame(self)
        right_container.pack(fill=BOTH, side=RIGHT, expand=False)
        self.md_panel = MetadataPanel(right_container)
        self.md_panel.pack(fill=BOTH, expand=True, side=TOP)
        Button(
            right_container,
            text="To Exports    →",
            command=lambda: self.master.select(1),
        ).pack(fill=X, side=BOTTOM)

    def __on_table_click(self, event):
        """Handle clicks on the table."""

        elem = self.treeview.identify_region(event.x, event.y)

        if elem == "heading":
            # sort by selected column
            col = self.treeview.identify_column(event.x)
            self.table_sort(col)

    def __on_table_select(self, event):
        if len(self.treeview.selection()) == 0:
            return
        id = self.treeview.selection()[-1]
        self.md_panel.set_song(db.metadata[id])
        self.refresh_lbl_selected()

    def refresh_lbl_selected(self):
        """Refresh the label that shows how many songs are selected."""
        self.lbl_selected.configure(
            text=(
                f"{len(self.treeview.selection())}/{len(self.treeview.get_children())}"
                f" song{"s" if len(self.treeview.selection()) != 1 else ""} selected for export"
            )
        )

    def refresh_jacket_previews(self):
        """Refresh the jacket previews."""
        self.md_panel.jackets.clear()
        for id, img in db.jacket_preview.items():
            self.md_panel.jackets[id] = ImageTk.PhotoImage(img)

    def table_clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def table_populate(self):
        """Populate the table with songs."""
        self.table_clear()

        for song in db.metadata.values():
            if (
                self.filter_game.get() != "None"
                and song.version != game_to_version[self.filter_game.get()]
            ):
                continue

            self.treeview.insert(
                "",
                "end",
                id=song.id,
                values=(song.id, song.name, song.artist, category_index[song.genre_id]),
            )

        self.table_sort("id")
        self.refresh_lbl_selected()

    def table_sort(self, col: str):
        """Sort the table by a column."""
        rows = [
            (self.treeview.set(item, col).lower(), item)
            for item in self.treeview.get_children("")
        ]

        if col == self.__table_cur_col_sort:
            self.__table_rev_sort = not self.__table_rev_sort
        else:
            self.__table_rev_sort = False

        if col == "#2":
            rows.sort(
                reverse=self.__table_rev_sort, key=lambda it: db.metadata[it[1]].rubi
            )
        else:
            rows.sort(reverse=self.__table_rev_sort)

        for index, (values, item) in enumerate(rows):
            self.treeview.move(item, "", index)
            self.treeview.item(item, tags=("oddrow",) if index % 2 else ())

        self.__table_cur_col_sort = col
