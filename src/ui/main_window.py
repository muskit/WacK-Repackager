from __future__ import annotations
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from typing import Type

import config

from .data_setup import DataSetupWindow
from .welcome_window import WelcomeWindow
from .about import AboutWindow

from .tabs.listing_tab import ListingTab
from .tabs.export_tab import ExportTab


class MainWidget(Notebook):
    instance: MainWidget = None

    def __init__(self, master):
        MainWidget.instance = self
        super().__init__(master)
        self.__init_widgets()
        self.bind("<<NotebookTabChanged>>", self.__on_tab_change)

    def __init_widgets(self):
        self.listing_tab = ListingTab(self)
        self.export_tab = ExportTab(self)

        self.add(self.listing_tab, text="Songs")
        self.add(self.export_tab, text="Export")

    def __on_tab_change(self, event):
        match self.index("current"):
            case 1:
                self.export_tab.refresh()


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("WacK Repackager")
        self.geometry("1024x610")
        self.minsize(900, 610)
        self.protocol("WM_DELETE_WINDOW", self.__exit)  # upon closing the window (X)

        self.__init_widgets()
        self.center_to_screen()
        self.after(100, self.__try_welcome)

    def __init_widgets(self):
        # menu bar
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Data Setup...", command=self.show_data_setup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.__exit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(
            label="Open Welcome Screen",
            command=lambda: self.show_and_focus_toplevel(
                WelcomeWindow, true_welcome=False
            ),
        )
        about_menu.add_separator()
        about_menu.add_command(
            label="About", command=lambda: self.show_and_focus_toplevel(AboutWindow)
        )
        menu_bar.add_cascade(label="About", menu=about_menu)

        self.config(menu=menu_bar)

        # tabbed widget
        tabbed = MainWidget(self)
        tabbed.pack(expand=1, fill="both")

    def __try_welcome(self):
        if not config.cfg_file_loaded:
            self.show_and_focus_toplevel(WelcomeWindow)
            self.show_data_setup(run_tasks=True, show_picker=True)
        else:
            self.show_data_setup(run_tasks=True, show_picker=False)

    def center_to_screen(self):
        """Center window to screen."""
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        size = tuple(int(_) for _ in self.geometry().split("+")[0].split("x"))
        x = screen_width / 2 - size[0] / 2
        y = screen_height / 2 - size[1] / 2

        self.geometry("+%d+%d" % (x, y))

    def center_toplevel(self, toplevel: Toplevel):
        """Center a toplevel relative to self."""
        self.update_idletasks()
        toplevel.update_idletasks()

        x, y = self.winfo_x(), self.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        tl_w = toplevel.winfo_width()
        tl_h = toplevel.winfo_height()
        dx, dy = w / 2 - tl_w / 2, h / 2 - tl_h / 2
        toplevel.geometry("%dx%d+%d+%d" % (tl_w, tl_h, x + dx, y + dy))

    def show_and_focus_toplevel(self, TLClass: Type[Toplevel], *args, **kwargs):
        win = TLClass(self, *args, **kwargs)
        win.transient(self)
        win.grab_set()
        win.focus_force()
        self.center_toplevel(win)
        self.wait_window(win)

    def show_data_setup(self, run_tasks=False, show_picker=False):
        self.show_and_focus_toplevel(
            DataSetupWindow, run_tasks=run_tasks, show_file_picker=show_picker
        )
        # refresh listing tab

    def __exit(self):
        if ExportTab.instance.working:
            if not messagebox.askokcancel(
                "Exit Application",
                "Are you sure you want to exit? This will cancel any ongoing exports.",
            ):
                return
        config.save()
        self.destroy()
