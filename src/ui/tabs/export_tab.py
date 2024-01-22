from __future__ import annotations

from enum import IntEnum, StrEnum
from queue import Queue, Empty
from threading import Thread
from typing import Any
import ffmpeg

from tkinter import *
from tkinter import filedialog, messagebox, font as tkFont
from tkinter.ttk import *
from PIL import ImageTk

from util import *
import config
import data.database as db
import data.metadata as md
from ui import data_setup
from .listing_tab import ListingTab
from export import export_song


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

        self.ui_queue: Queue[(str, Any)] = Queue()
        self.__cur_export_thread: Thread = None

        super().__init__(master)

        self.export_path = StringVar(self, config.export_path)
        self.export_path.trace_add("write", self.__action_path_change)
        self.export_group = IntVar(self, 0)
        self.export_group.trace_add("write", self.__refresh_exports_table)
        self.working = False
        self.just_finished = False

        # progress tracking
        self.songs_queue: Queue[str] = Queue(maxsize=400)
        self.__pbar_val = IntVar(self, 0)
        self.progress_image = {
            "success": ImageTk.PhotoImage(data_setup.ProgressIcon.image["complete"]),
            "alert": ImageTk.PhotoImage(data_setup.ProgressIcon.image["alert"]),
            "error": ImageTk.PhotoImage(data_setup.ProgressIcon.image["error"]),
        }
        self.songs_processed: set[str] = set()
        self.song_alerts: dict[str, list[str]] = dict()
        self.song_errors: dict[str, str] = dict()

        # export options
        self.option_game_subfolders = BooleanVar(self)
        self.option_delete_originals = BooleanVar(self)
        self.option_convert_audio = BooleanVar(self)
        self.option_convert_audio.trace_add("write", self.__action_audio_conv_change)
        self.option_audio_target = StringVar(self, AudioConvertTarget.MP3)
        self.option_exclude_videos = BooleanVar(self)
        self.option_threads = IntVar(self, 1)

        self.__init_widgets()
        self.after(200, self.__event_queue_process)

    def __init_widgets(self):
        ## RIGHT SIDE (export) ##
        self.right_container = Frame(self, relief="flat")
        self.right_container.pack(side=RIGHT, fill=BOTH, expand=True)

        export_top = Frame(self.right_container)
        export_top.pack(fill=BOTH, expand=True)

        # Table of songs to be exported
        tv_scr = Scrollbar(export_top, orient=VERTICAL)
        self.treeview = Treeview(
            export_top,
            yscrollcommand=tv_scr.set,
            columns=("id", "title", "artist", "game"),
            selectmode="none",
        )
        tv_scr.configure(command=self.treeview.yview)
        tv_scr.pack(fill=Y, side=RIGHT)
        self.treeview.pack(fill=BOTH, expand=True, side=LEFT)
        # self.treeview.tag_configure("oddrow", background="#f0f0ff")
        self.treeview.tag_configure("done", foreground="#bbbbbb")
        self.treeview.bind("<Motion>", self.__action_table_hover)

        self.treeview.column("#0", width=75, stretch=False)
        self.treeview.heading("id", text="ID", anchor=CENTER)
        self.treeview.column("id", width=75, stretch=False, anchor=CENTER)
        self.treeview.heading("title", text="Song Name", anchor=W)
        self.treeview.heading("artist", text="Artist", anchor=W)
        self.treeview.heading("game", text="Game", anchor=W)
        self.treeview.column("game", width=150, stretch=False)

        # Export path and button
        export_btm = Frame(self.right_container)
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

        self.right_container = Frame(export_btm)
        self.right_container.pack(fill=X, expand=True, side=RIGHT, pady=(13, 0))
        self.__pbar_export = Progressbar(
            self.right_container,
            orient=HORIZONTAL,
            mode="determinate",
            variable=self.__pbar_val,
        )
        self.__pbar_export.pack(side=LEFT, fill=X, expand=True, padx=(10, 3))

        self.__btn_export = Button(
            self.right_container, text="Export", command=self.__action_export
        )
        self.__btn_export.pack(side=RIGHT, anchor="s")

        ## LEFT SIDE (options) ##
        self.left_container = Frame(self, relief="solid", width=250)
        self.left_container.pack_propagate(0)
        self.left_container.pack(side=LEFT, fill=Y)
        Label(self.left_container, text="Export Options", background="lightgray").pack(
            fill=X, padx=1, pady=1
        )

        # Export group options
        export_group_options = LabelFrame(self.left_container, text="Group to Export")
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

        audio_conv_options = LabelFrame(self.left_container, text="Audio Conversion")
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
        self.combobox_audio_conv_target.pack(pady=(0, 5))

        Checkbutton(
            self.left_container,
            text="Exclude Videos",
            variable=self.option_exclude_videos,
        ).pack(anchor="w", padx=5)

        Checkbutton(
            self.left_container,
            text="Export to Subfolders by Game",
            variable=self.option_game_subfolders,
        ).pack(anchor="w", padx=5)

        Checkbutton(
            self.left_container,
            text="Delete Original Files",
            variable=self.option_delete_originals,
        ).pack(anchor="w", padx=5)

        threads_container = Frame(self.left_container)
        threads_container.pack(fill=X, padx=(5, 15), pady=(10, 20))
        Label(threads_container, text="Threads").pack(anchor="w", padx=5)
        Entry(threads_container, textvariable=self.option_threads, width=8).pack(
            side=LEFT, padx=5
        )

        export_msg_container = LabelFrame(self.left_container, text="Warnings/Errors")
        export_msg_container.pack(fill=BOTH, expand=True, padx=5, pady=10)
        self.lbl_messages = Message(
            export_msg_container,
            width=220,
            text="Hover over a song to see its messages from exporting.",
            anchor=NW,
        )
        self.lbl_messages.pack(anchor="w", padx=5, fill=BOTH, expand=True)
        f = tkFont.nametofont("TkDefaultFont").actual()
        self.lbl_song_stats = Label(
            self.left_container,
            text="0/0 songs processed",
            font=(f["family"] + " Italic", f["size"], ""),
        )
        self.lbl_song_stats.pack(anchor=SE, padx=5, pady=(0, 5))

    def __event_queue_process(self):
        try:
            while True:
                msg = self.ui_queue.get_nowait()
                match msg[0]:
                    case "p_bar":
                        # msg[1]: int (step)
                        # msg[2]: int (prog)
                        # msg[3]: int (max)
                        self.set_pbar(msg[1], msg[2], msg[3])
                    case "table_status":
                        # msg[1]: str (id)
                        # msg[2]: str ("working", "success", "alert", "error")
                        if msg[2] != "working":
                            self.treeview.item(
                                msg[1],
                                tags="done",
                                image=self.progress_image[msg[2]],
                                text="",
                            )
                            self.treeview.selection_remove(msg[1])
                        else:
                            self.treeview.item(
                                msg[1],
                                text="WORKING...",
                                tags=None,
                                image=None,
                            )
                            self.treeview.selection_add(msg[1])
                    case "finished":
                        self.__export_end(abort=False)
                self.__refresh_song_stats()
        except Empty:
            pass

        self.after(200, self.__event_queue_process)

    def __refresh_exports_table(self, *_):
        self.treeview.delete(*self.treeview.get_children())

        match self.export_group.get():
            case ExportGroup.ALL:
                for i, song in enumerate(db.metadata.values()):
                    self.treeview.insert(
                        "",
                        "end",
                        iid=song.id,
                        tags=("oddrow" if i % 2 == 1 else ""),
                        values=(
                            song.id,
                            song.name,
                            song.artist,
                            md.version_to_game[song.version],
                        ),
                    )
            case ExportGroup.SELECTED:
                for i, id in enumerate(ListingTab.instance.treeview.selection()):
                    song = db.metadata[id]
                    self.treeview.insert(
                        "",
                        "end",
                        tags=("oddrow" if i % 2 == 1 else ""),
                        iid=song.id,
                        values=(
                            song.id,
                            song.name,
                            song.artist,
                            md.version_to_game[song.version],
                        ),
                    )
            case ExportGroup.FILTERED:
                for i, id in enumerate(ListingTab.instance.treeview.get_children()):
                    song = db.metadata[id]
                    self.treeview.insert(
                        "",
                        "end",
                        tags=("oddrow" if i % 2 == 1 else ""),
                        iid=song.id,
                        values=(
                            song.id,
                            song.name,
                            song.artist,
                            md.version_to_game[song.version],
                        ),
                    )
        self.__refresh_song_stats()

    def __refresh_song_stats(self):
        self.lbl_song_stats.configure(
            text=f"{len(self.songs_processed)}/{len(self.treeview.get_children())} songs processed"
        )

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

    def __action_table_hover(self, event):
        id = self.treeview.identify_row(event.y)
        if id == "":
            return

        txt = f"[{id}]\n"
        if id in self.song_alerts:
            for m in self.song_alerts[id]:
                txt += f" • {m}\n"
            self.lbl_messages.configure(text=txt)
        elif id in self.song_errors:
            txt += f"Error: {self.song_errors[id]}"
            self.lbl_messages.configure(text=txt)
        else:
            self.lbl_messages.configure(text=f"{txt}No messages.")

    ## EXPORT BUTTON ACTIONS ##
    def __action_export(self, *_):
        self.working = True

        # disable widgets
        # TODO: rename to "Abort" and enable
        self.__btn_export.configure(
            text="Exporting", command=self.__action_abort, state=DISABLED
        )
        self.__btn_browse.configure(state=DISABLED)
        self.__entry_path.configure(state=DISABLED)
        disable_children_widgets(self.left_container)
        enable_children_widgets(self.lbl_messages.master)

        for id in self.treeview.get_children():
            self.songs_queue.put(id)

        self.start_export_thread()

    def __action_reset(self, *_):
        self.__btn_export.configure(text="Export", command=self.__action_export)
        enable_children_widgets(self.left_container)
        self.__btn_browse.configure(state=NORMAL)
        self.__entry_path.configure(state=NORMAL)
        self.__pbar_val.set(0)

        self.songs_processed.clear()
        self.song_alerts.clear()
        self.song_errors.clear()

        self.just_finished = False
        self.refresh()

    def __action_abort(self, *_):
        if messagebox.askokcancel(
            "Abort Export?",
            "Are you sure you want to abort the export?",
        ):
            self.__export_end(abort=True)

    def __export_end(self, abort: bool):
        self.__btn_export.configure(
            text="Reset", command=self.__action_reset, state=NORMAL
        )

        stats = (
            f"Processed {len(self.songs_processed)}/{len(self.treeview.get_children())} songs "
            f"with {len(self.song_alerts)} warnings "
            f"and {len(self.song_errors)} errors."
        )

        if not abort:
            messagebox.showinfo("Export Complete", stats)
        else:
            messagebox.showwarning("Export Aborted", stats)

        # TODO: abort export work threads if active

    def start_export_thread(self):
        """Export thread starter"""
        if self.__cur_export_thread is not None:
            self.__cur_export_thread.join()
        self.__cur_export_thread = Thread(target=self.__export_thread)

        self.__cur_export_thread.start()

    def __export_thread(self):
        # create worker threads
        work_threads = []
        for i in range(self.option_threads.get()):
            t = Thread(target=self.__export_thread_worker)
            t.start()
            work_threads.append(t)

        # wait for worker threads to finish
        for t in work_threads:
            t.join()

        print("Export thread finished")
        self.working = False
        self.just_finished = True
        self.ui_queue.put_nowait(("finished",))

    def __export_thread_worker(self):
        total = len(self.treeview.get_children())
        while True:
            try:
                id = self.songs_queue.get(block=False)
                self.ui_queue.put_nowait(("table_status", id, "working"))

                # Export
                song = db.metadata[id]
                print(f"Exporting {id} ({song.artist} - {song.name})...")
                try:
                    alerts = export_song(song)
                except Exception as e:
                    print(f"Error exporting {id}: {e}")
                    self.song_errors[id] = str(e)
                    self.ui_queue.put_nowait(("table_status", id, "error"))
                    self.songs_processed.add(id)
                    continue
                self.songs_processed.add(id)

                if len(alerts) == 0:
                    # no issues
                    self.ui_queue.put_nowait(("table_status", id, "success"))
                    self.ui_queue.put_nowait(("p_bar", 1, None, total))
                else:
                    self.ui_queue.put_nowait(("table_status", id, "alert"))
                    print(f"Exported with warnings:")
                    for a in alerts:
                        print(f"\t{a}")
                    self.song_alerts[id] = alerts
            except Empty:
                break

    def set_pbar(self, step: int = None, prog: int = None, maximum: int = None):
        if maximum is not None:
            self.__pbar_export["max"] = maximum

        if prog is not None:
            self.__pbar_val.set(prog)

        if step is not None:
            self.__pbar_val.set(self.__pbar_val.get() + step)

    def refresh(self):
        """Called upon tab being visible."""
        if (self.working) or (not self.working and self.just_finished):
            return

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
