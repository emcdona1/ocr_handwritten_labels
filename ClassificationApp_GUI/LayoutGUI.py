import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Style, Combobox

from django.conf.locale import tk

from ClassificationApp_GUI.ProcessTag import OpenTagId
from DatabaseProcessing.DatabaseProcessing import GetImportedTagTuples


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

    ###############Panels#####################

    windowWidth = leftPanelWidthForTagList_width + rightPanelForImageStatusAndOutput_width
    #main window
    root.geometry = str(windowWidth) + "x" + str(windowHeight)
    root.wm_geometry(root.geometry)
    root.resizable(0,0)
    root.config(background="white")
    #Left Panel for the tag list
    leftPanelFrame = Frame(root, width=leftPanelWidthForTagList_width,background="gray")
    leftPanelFrame.pack(anchor=NW, expand=True, side=LEFT )
    # Left Panel DDL select date
    selectDateFrame = Frame(leftPanelFrame, width=leftPanelWidthForTagList_width, background="gray34")
    selectDateFrame.pack(anchor=NW, expand=True, side=TOP)
    root.selectDateCBox = Combobox(selectDateFrame, values=[], font=("Courier", 14), state="readonly")
    root.selectDateCBox.bind('<<ComboboxSelected>>', lambda event, x=root: RefreshFilteredList(event, x))
    root.selectDateCBox.pack()

    # Left Panel Tag List frame
    selectTagFrame = Frame(leftPanelFrame, width=leftPanelWidthForTagList_width,
                                background="gray90")
    selectTagFrame.pack(anchor=SW, expand=True, side=BOTTOM)
    root.selectTagListBox = Listbox(selectTagFrame, font=("Courier", 15), height=1000, bd=0, background=None)
    root.selectTagListBox.pack(side=LEFT, fill=BOTH, padx=0, pady=1, expand=True)
    root.selectTagListBox.bind('<<ListboxSelect>>', lambda event, x=root: TagSelected(event, x))

    scrollbar = Scrollbar(selectTagFrame, bd=0, width=5)
    root.selectTagListBox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=root.selectTagListBox.yview)
    scrollbar.pack(side=RIGHT, fill=BOTH, expand=True)

    #Right Panel for the image Area, status, and output area
    rightPanelFrame = Frame(root, height=windowHeight, background="yellow")
    rightPanelFrame.pack(anchor=NE, expand=TRUE,fill=BOTH, side=RIGHT)
    #Right Panel canvas frame
    root.imageCanvasFrame = Frame(rightPanelFrame, height=imageCanvasAreaHeight,
                              background="gray")
    root.imageCanvasFrame.pack(anchor=NE, expand=True, fill=BOTH,side=TOP)
    # status bar
    statusBarFrame = Frame(rightPanelFrame, height=statusAreaHeight,background="gray94")
    statusBarFrame.pack(anchor=NW, expand=True,fill=BOTH, side=TOP)
    wordStatusFrame = Frame(statusBarFrame, height=50, bd=1, background="gray95")
    wordStatusFrame.pack(anchor=NW, expand=False, fill=BOTH, side=TOP)

    root.wordStatusLabel = Label(wordStatusFrame, text="Please import or open image file to continue!",
                                 background="gray95", justify="left", bd=1, anchor="nw",
                                 font=("Courier", 14))
    root.wordStatusLabel.pack(expand=True, fill=BOTH, side=LEFT)

    fileInfoFrame = Frame(statusBarFrame, height=50, bd=1, background="gray88")
    fileInfoFrame.pack(anchor=NW, expand=False, fill=X, side=BOTTOM)
    root.fileInfoLabel = Label(fileInfoFrame, text="", background="gray88", justify="left", bd=1, anchor="nw",
                               font=("Courier", 14))
    root.fileInfoLabel.pack(expand=True, fill=BOTH, side=LEFT)

    # output area
    outputAreaFrame = Frame(rightPanelFrame, height=(windowHeight - imageCanvasAreaHeight-statusAreaHeight),
                                background="white")
    outputAreaFrame.pack(anchor=SW, expand=True,fill=BOTH, side=BOTTOM)

    root.outputField = ScrolledText(outputAreaFrame, font=("Courier", 16), bd=0, highlightthickness=0)
    root.outputField.pack(padx=0, pady=2, fill=BOTH, expand=True)


def TagSelected(evt,root):
    try:
        w = evt.widget
        index=int(w.curselection()[0])
        selectedItem=(root.importedTags[index])
        root.tagId=selectedItem[0]
        root.importedDate=selectedItem[1]
        root.imagePath=selectedItem[2]
        OpenTagId(root,root.tagId)
    except:
        pass
    pass

def InitializeImportedListCBox(root):
    root.importedTags = GetImportedTagTuples()
    root.selectDateCBox['values']=GetImportedDates(root)
    root.selectDateCBox.set("Filter: None")
    InitializeTagListBox(root)
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
