from tkinter import *
from tkinter.scrolledtext import ScrolledText

from Helper.GetWordsInformation import GetDescriptionFromDataBlocks


def CreateOutputFrameToDisplayInfo(root, outputFrame):
    outputFrame.configure(padx=10, pady=10)
    root.outputField = ScrolledText(outputFrame, height=15, width=75)

    root.outputField.configure(font=("Courier", 16), padx=10, pady=10)
    root.outputField.pack(anchor="nw", expand=1)
    # textfield.grid(row=0,column=0,sticky="nsew")


def UpdateOutput(root, **kw):
    ClearOutput(root)
    type = kw.pop('type', "corrected")
    useHint = kw.pop('useHint', 0)
    data = "######### Data #########\n" + \
           GetDescriptionFromDataBlocks(type, root.sdb, useHint)
    classifiedData = "\n\n######### Classified Information #########\n" + \
                     GetDescriptionFromDataBlocks('classified', root.sdb, 1, root.WordCategories)
    AppendToOutputArea(root, data)
    AppendToOutputArea(root, classifiedData)


def AppendToOutputArea(root, value):
    root.outputField.insert('insert', value)


def ClearOutput(root):
    root.outputField.delete('1.0', END)
