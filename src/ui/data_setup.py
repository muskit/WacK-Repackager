from tkinter import *
from tkinter.ttk import *


class DataSetupWidget(Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.pack()

        l = Label(self, text="Hello")
        l.pack()
