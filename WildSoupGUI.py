import sys
try:
    from Tkinter import *
    from WildSoup import WildSoup
    import ttk
except ImportError as ie:
    print str(ie)
    sys.exit("To install a module: pip install moduleName")

class Gui(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.output()

    def output():
        pass
