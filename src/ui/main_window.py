from tkinter import *
from tkinter.ttk import *

import config

from .tabs.listing import ListingTab
from .tabs.export import ExportTab

from .welcome_window import WelcomeWindow


class MainWidget(Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.__init_widgets()

    def __init_widgets(self):
        listing_tab = ListingTab(self)
        export_tab = ExportTab(self)

        self.add(listing_tab, text="Songs")
        self.add(export_tab, text="Export")


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("WacK Repackager")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.__exit)  # upon closing the window (X)
        self.__init_widgets()
        self.__post_init()

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

    def __init_widgets(self):
        # menu bar
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open folder...", command=None)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.__exit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="Open Welcome Screen", command=self.__show_welcome)
        about_menu.add_separator()
        about_menu.add_command(label="About", command=None)
        menu_bar.add_cascade(label="About", menu=about_menu)

        self.config(menu=menu_bar)

        # tabbed widget
        tabbed = MainWidget(self)
        tabbed.pack(expand=1, fill="both")

    def __post_init(self):
        self.center_to_screen()
        if not config.cfg_file_loaded:
            print("First time opening!")
            self.__show_welcome()

    def __show_welcome(self):
        welcome = WelcomeWindow(self)
        welcome.transient(self)
        welcome.grab_set()
        self.center_toplevel(welcome)
        self.wait_window(welcome)

    def __exit(self):
        print("exit event invoked!")
        # config.save()
        self.destroy()
