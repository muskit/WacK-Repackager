from __future__ import annotations

from enum import Enum

from tkinter import *
from tkinter.ttk import *

from data.metadata import SongMetadata, category_index


class ListingTab(Frame):
    instance: ListingTab = None

    def __init__(self, master):
        ListingTab.instance = self
        super().__init__(master)
        self.__init_widgets()

    def __init_widgets(self):
        table_container = Frame(self)
        table_container.pack(fill=BOTH, expand=True, side=LEFT)
        self.treeview = Treeview(
            table_container, columns=("id", "title", "artist", "genre")
        )
        self.treeview.column("#0", width=0, stretch=False)
        self.treeview.pack(fill=BOTH, expand=True)

        self.treeview.heading("id", text="ID", anchor=CENTER)
        self.treeview.column("id", width=75, stretch=False, anchor=CENTER)
        self.treeview.heading("title", text="Song Name", anchor=W)
        self.treeview.heading("artist", text="Artist", anchor=W)
        self.treeview.heading("genre", text="Genre", anchor=W)
        self.treeview.column("genre", width=150, stretch=False)

        metadata_container = Frame(self, width=240)
        metadata_container.pack(fill=BOTH, side=RIGHT)
        # TODO: add metadata widgets

    def table_clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def table_populate(self, songs: dict[str, SongMetadata]):
        """Populate the table with songs."""
        self.table_clear()

        for song in songs.values():
            self.treeview.insert(
                "",
                "end",
                values=(song.id, song.name, song.artist, category_index[song.genre_id]),
            )

        self.table_sort("id")

    def table_sort(self, col: str, reverse: bool = False):
        """Sort the table by a column."""
        rows = [
            (self.treeview.set(item, col).lower(), item)
            for item in self.treeview.get_children("")
        ]
        rows.sort()

        for index, (values, item) in enumerate(rows):
            self.treeview.move(item, "", index)
