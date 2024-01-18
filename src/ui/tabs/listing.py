from __future__ import annotations

from enum import Enum

from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk

import data.database as db
from data.metadata import SongMetadata, category_index


class MetadataPanel(Frame):
    img_jacket_placeholder = Image.open("./assets/jacket-placeholder.png").resize(
        (200, 200)
    )

    def __init__(self, master):
        super().__init__(master, width=220, relief=GROOVE)
        self.pack_propagate(False)
        self.init_widgets()

    def init_widgets(self):
        self.image = ImageTk.PhotoImage(self.img_jacket_placeholder)
        self.md_img = Label(self, image=self.image)
        self.md_img.pack(pady=10)
        Label(self, text="test").pack()

    def set_song(self, song: SongMetadata):
        path = song.jacket
        print(path)
        self.image = ImageTk.PhotoImage(Image.open(path).resize((200, 200)))
        self.md_img.configure(image=self.image)


class ListingTab(Frame):
    instance: ListingTab = None

    def __init__(self, master):
        ListingTab.instance = self
        super().__init__(master)
        self.__init_widgets()
        self.__table_cur_col_sort: str = None
        self.__table_rev_sort: bool = False

    def __init_widgets(self):
        # Table of songs in database
        table_container = Frame(self)
        table_container.pack(fill=BOTH, expand=True, side=LEFT)
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

        self.md_panel = MetadataPanel(self)
        self.md_panel.pack(fill="both", side=RIGHT, expand=False)

    def __on_table_click(self, event):
        """Handle clicks on the table."""

        elem = self.treeview.identify_region(event.x, event.y)

        if elem == "heading":
            # sort by selected column
            col = self.treeview.identify_column(event.x)
            self.table_sort(col)

    def __on_table_select(self, event):
        id = self.treeview.selection()[-1]
        self.md_panel.set_song(db.metadata[id])

    def table_clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def table_populate(self, songs: dict[str, SongMetadata]):
        """Populate the table with songs."""
        self.table_clear()

        for song in songs.values():
            self.treeview.insert(
                "",
                "end",
                id=song.id,
                values=(song.id, song.name, song.artist, category_index[song.genre_id]),
            )

        self.table_sort("id")

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

        rows.sort(reverse=self.__table_rev_sort)

        for index, (values, item) in enumerate(rows):
            self.treeview.move(item, "", index)
            self.treeview.item(item, tags=("oddrow",) if index % 2 else ())

        self.__table_cur_col_sort = col
