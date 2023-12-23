from tkinter import *
from tkinter.ttk import *


class WelcomeWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Welcome")
        self.geometry("500x500")
        self.resizable(False, False)
