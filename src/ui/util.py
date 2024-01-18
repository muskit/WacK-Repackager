from tkinter import *
import tkinter.font as tkFont
from tkinter.ttk import *


# https://stackoverflow.com/questions/51143777/display-three-dots-in-the-end-of-a-tkinter-label-text
def try_ellipsis(label: Label):
    l_font = tkFont.Font(font=label["font"]).actual()

    font = tkFont.nametofont("TkDefaultFont").copy()
    font.configure(size=l_font["size"])

    text = label["text"]
    max_width = label.winfo_width()
    text_width = font.measure(text)
    if text_width <= max_width:
        # the original text fits; no need to add ellipsis
        label.configure(text=text)
    else:
        # the original text won't fit. Keep shrinking
        # until it does
        while text_width > max_width and len(text) > 1:
            text = text[:-1]
            text_width = font.measure(text + "...")
        label.configure(text=text + "...")
