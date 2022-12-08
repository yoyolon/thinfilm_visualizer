from app import *
import tkinter as tk
import sv_ttk


if __name__=="__main__":
    window = tk.Tk() 
    app = App(window)
    sv_ttk.set_theme("dark")
    app.mainloop()