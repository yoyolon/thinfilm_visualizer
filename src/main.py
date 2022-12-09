import sv_ttk
import tkinter as tk
from app import *


if __name__=="__main__":
    window = tk.Tk() 
    app = App(window)
    sv_ttk.set_theme("dark")
    app.mainloop()