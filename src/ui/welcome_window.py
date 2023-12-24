from tkinter import *
from tkinter.ttk import *

import webbrowser


class WelcomeWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Welcome")
        self.geometry("350x130")
        self.resizable(False, False)
        self.__layout_widgets()

    def __layout_widgets(self):
        i = Label(self, image="::tk::icons::information")
        i.pack(anchor="center", pady=(12, 0))
        l = Label(
            self,
            text="Before proceeding, please have files prepared as outlined by the HOWTO.",
            wraplength=320,
            justify="center",
        )
        l.pack(anchor="center")

        # buttons
        btn_container = Frame(self)
        btn_container.pack(expand=True)

        Button(btn_container, text="Continue", command=self.__action_continue).pack(
            side="left"
        )
        Button(btn_container, text="View HOWTO", command=self.__action_howto).pack(
            side="left"
        )
        Button(
            btn_container, text="Exit Application", command=self.__action_exit_app
        ).pack(side="left")

    def __action_continue(self):
        self.destroy()

    def __action_howto(self):
        webbrowser.open("https://github.com/muskit/WacK-Repackager/blob/main/HOWTO.md")

    def __action_exit_app(self):
        self.destroy()
        self.master.destroy()
