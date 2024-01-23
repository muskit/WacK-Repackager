from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont
import webbrowser

from PIL import Image, ImageTk

import util


class About(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack_propagate(False)
        self.init_widgets()

    def init_widgets(self):
        with open(util.resource_path("version.txt")) as f:
            version = f.read().strip()

        f = tkFont.nametofont("TkDefaultFont").actual()
        Label(self, text="WacK Repackager", font=(f["family"], 24)).pack()

        Label(self, text=f"v{version}").pack(pady=(0, 15))

        Label(
            self,
            text="A tool for repacking WACCA songs.",
            anchor=CENTER,
        ).pack(fill=X, padx=40)

        btn_container = Frame(self)
        btn_container.pack(expand=True)

        self.img_github = ImageTk.PhotoImage(
            Image.open(util.resource_path("assets/github.png")).resize(
                (32, 32), Image.BICUBIC
            )
        )
        self.img_twitter = ImageTk.PhotoImage(
            Image.open(util.resource_path("assets/twitter.png")).resize(
                (32, 32), Image.BICUBIC
            )
        )
        Button(
            btn_container,
            image=self.img_github,
            command=lambda: webbrowser.open(
                "https://github.com/muskit/WacK-Repackager"
            ),
        ).pack(side="left")
        Button(
            btn_container,
            image=self.img_twitter,
            command=lambda: webbrowser.open("https://twitter.com/SlappyFlye"),
        ).pack(side="left")


class AboutWindow(Toplevel):
    def __init__(self, master=None):
        super().__init__(master=None)
        self.title("About")
        self.resizable(False, False)
        self.geometry("400x175")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.init_widgets()

    def init_widgets(self):
        self.about = About(self)
        self.about.pack(fill=BOTH, expand=True)

    def close(self):
        self.destroy()
