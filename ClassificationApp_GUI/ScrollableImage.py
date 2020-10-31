import tkinter
from tkinter import *

from PIL.ImageTk import PhotoImage


class ScrollableImage(tkinter.Frame):
    def __init__(self, master=None, **kw):
        root = kw.pop('root', None)
        self.image = PhotoImage(file=root.tagPath)
        sw = kw.pop('scrollbarwidth', 10)
        w = kw.pop('width', 0)
        h = kw.pop('height', 0)
        super(ScrollableImage, self).__init__(master=master, **kw)
        self.cnvs = tkinter.Canvas(self, highlightthickness=0, background="gray", width=w-sw,height=h-sw, **kw)
        self.cnvs.image = self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        # Vertical and Horizontal scrollbars
        self.v_scroll = tkinter.Scrollbar(self, orient='vertical', width=sw)
        self.h_scroll = tkinter.Scrollbar(self, orient='horizontal', width=sw)
        # Grid and configure weight.
        self.cnvs.grid(row=0, column=0, sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Set the scrollbars to the canvas
        self.cnvs.config(xscrollcommand=self.h_scroll.set,
                         yscrollcommand=self.v_scroll.set)
        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.cnvs.yview)
        self.h_scroll.config(command=self.cnvs.xview)
        # Assign the region to be scrolled
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))
        self.cnvs.bind_class(self.cnvs, "<MouseWheel>", self.MouseScroll)
        root.image_window = self
        root.image_window.grid(row=0, column=0)

    def UpdateImage(self, root):
        self.image = root.image
        self.cnvs.image = self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        root.image_window = self
        root.image_window.grid(row=0, column=0)

    def MouseScroll(self, evt):
        if evt.state == 0:
            self.cnvs.yview_scroll(-1 * (evt.delta), 'units')  # For MacOS
            self.cnvs.yview_scroll(int(-1 * (evt.delta / 120)), 'units')  # For windows
        if evt.state == 1:
            self.cnvs.xview_scroll(-1 * (evt.delta), 'units')  # For MacOS
            self.cnvs.xview_scroll(int(-1 * (evt.delta / 120)), 'units')  # For windows

def AddElementImageCanvas(root):
    root.scrollableImage = ScrollableImage(root.imageCanvasFrame, root=root, scrollbarwidth=5,
                                           width=root.canvasWidth,
                                           height=root.canvasHeight)
    pass
