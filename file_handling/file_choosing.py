import tkinter
from tkinter import filedialog

root = tkinter.Tk()
files = filedialog.askopenfilenames(parent=root,title='Choose files')
files = root.tk.splitlist(files)
