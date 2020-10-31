import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Style, Combobox

from django.conf.locale import tk

from ClassificationApp_GUI.ProcessTag import OpenTagId
from ClassificationApp_GUI.ToolTip import ToolTip


def CreateLayout(root):
    ###############sizes#############
    windowHeight = 600
    leftPanelWidthForTagList_width = 180
    rightPanelForImageStatusAndOutput_width = 600
    ddlBoxHeight=30
    imageCanvasAreaHeight=350
    statusAreaHeight=60
    root.tagListBoxHeight=windowHeight-ddlBoxHeight
    root.canvasHeight=imageCanvasAreaHeight
    root.canvasWidth=rightPanelForImageStatusAndOutput_width
    ############# Style########


    ###############Panels#####################

    windowWidth = leftPanelWidthForTagList_width + rightPanelForImageStatusAndOutput_width
    #main window
    root.geometry = str(windowWidth) + "x" + str(windowHeight)
    root.wm_geometry(root.geometry)
    root.resizable(0,0)
    root.config(background="white")
    #Left Panel for the tag list
    leftPanelFrame = Frame(root, height=windowHeight, width=leftPanelWidthForTagList_width,background="gray")
    leftPanelFrame.pack(anchor=NW, expand=True, side=LEFT )
    # Left Panel DDL frame
    root.selectDateFrame = Frame(leftPanelFrame, height=ddlBoxHeight, width=leftPanelWidthForTagList_width, background="gray34")
    root.selectDateFrame.pack(anchor=NW, expand=True, side=TOP)
    # Left Panel Tag List frame
    root.selectTagFrame = Frame(leftPanelFrame, height=(windowHeight - ddlBoxHeight), width=leftPanelWidthForTagList_width,
                                background="gray90")
    root.selectTagFrame.pack(anchor=SW, expand=True, side=BOTTOM)

    #Right Panel for the image Area, status, and output area
    rightPanelFrame = Frame(root, height=windowHeight, width=rightPanelForImageStatusAndOutput_width, background="green")
    rightPanelFrame.pack(anchor=NE, expand=True, side=RIGHT)
    #Right Panel canvas frame
    root.imageCanvasFrame = Frame(rightPanelFrame, height=imageCanvasAreaHeight, width=rightPanelForImageStatusAndOutput_width,
                              background="gray")
    root.imageCanvasFrame.pack(anchor=NE, expand=True, side=TOP)
    # Left Panel Tag List frame
    root.statusBarFrame = Frame(rightPanelFrame, height=statusAreaHeight,
                                  width=rightPanelForImageStatusAndOutput_width,
                                  background="gray94")
    root.statusBarFrame.pack(anchor=N, expand=True, side=TOP)

    root.outputAreaFrame = Frame(rightPanelFrame, height=(windowHeight - imageCanvasAreaHeight-statusAreaHeight),
                                width=rightPanelForImageStatusAndOutput_width,
                                background="white")
    root.outputAreaFrame.pack(anchor=SW, expand=True, side=BOTTOM)

def AddElementSelectDate(root):
    root.selectDateCBox = Combobox(root.selectDateFrame, values=[], font=("Courier", 14), width=19, state="readonly")
    root.selectDateCBox.bind('<<ComboboxSelected>>', lambda event, x=root: RefreshFilteredList(event, x))
    root.selectDateCBox.pack()
    pass

def AddElementSelectTag(root):
    root.selectTagListBox=Listbox(root.selectTagFrame,font=("Courier", 15), width=19, height=34,bd=0,background=None)
    root.selectTagListBox.pack(side=LEFT, fill=None, padx=1, pady=1,expand=True)
    root.selectTagListBox.bind('<<ListboxSelect>>', lambda event, x=root:TagSelected(event,x))

    scrollbar = Scrollbar(root.selectTagFrame, bd=0, width=5)
    root.selectTagListBox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=root.selectTagListBox.yview)
    scrollbar.pack(side=RIGHT, fill=BOTH)
    pass

def TagSelected(evt,root):
        w = evt.widget
        index=int(w.curselection()[0])
        selectedItem=(root.importedTags[index])
        root.tagId=selectedItem[0]
        root.importedDate=selectedItem[1]
        root.imagePath=selectedItem[2]
        OpenTagId(root,root.tagId)

def InitializeImportedListCBox(root):
    root.selectDateCBox['values']=GetImportedDates(root)
    root.selectDateCBox.set("Filter: None")
    pass

def InitializeTagListBox(root):
    root.selectTagListBox.delete(0, tkinter.END)
    for x in root.importedTags:
        root.selectTagListBox.insert(x[0]," "+x[2].split('/')[-1])
    pass

def RefreshFilteredList(event,root):
    selected=root.selectDateCBox.get()
    UpdateTagListBySelection(root,selected)
    pass

def GetImportedDates(root):
    dates=[x[1] for x in root.importedTags]
    dates.append("Filter: None")
    return sorted(list(set(dates)))
    pass

def UpdateTagListBySelection(root,selected):
    root.selectTagListBox.delete(0, tkinter.END)
    for x in root.importedTags:
        if x[1]==selected or selected=='Filter: None':
            root.selectTagListBox.insert(x[0], " " + x[2].split('/')[-1])
    pass

def AddElementStatusBar(root):
    root.statusBar = Label(root.statusBarFrame, text="", background="light gray", justify="left", bd=1, anchor="nw",
                           width=0,
                           height=4,
                           font=("Courier", 16))
    root.statusBar.pack(expand=True)

    pass

def AddElementOutputArea(root):
    pass

class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background='yellow', relief='solid', borderwidth=1,
                       font=("times", "8", "normal"))
        label.pack(ipadx=1)
    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

